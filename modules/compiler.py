import logging
import re
import pprint

# constants
INSTRUCT, SCORE, VOICE, OCTAVE, MUTATION = "instruct", "score", "voice", "octave", "mutation"
NOTES = ["ut", "re", "me", "fa", "sol", "la", "ut+", "re+", "me+", "fa+", "sol+", "la+", "-", ">"]

## MAIN FUNCTION ##
def process_file(filepath: str) -> dict | list:
    voices = []
    file_data = {"title": None, "composer": None, "letter": None}

    mode = None
    octave = None
    mutation = None
    chords = []
    duration = 1
    voice = -1

    with open(filepath, "r") as MUSIC_FILE:
        for line in MUSIC_FILE.readlines():
            # clean line for algorithm
            line = line.strip()
            if not line or line == "}" or line[0] == "#":
                continue
            tokens = line.split(" ")
            tokens = [token for token in tokens if token]


            # mode change
            if tokens[0].startswith("\\"):
                mode, octave, mutation, voice = change_mode(mode, tokens, voices, octave, mutation, voice)
                # error detected
                if mode == None: 
                    logging.error("mode not found")
                continue
            
            # process mode
            if mode == INSTRUCT:
                update_file_data(tokens, file_data)
            elif mode == VOICE:
                duration, chords = update_voices(tokens, voices[voice], octave, mutation, duration, chords)

    return file_data, voices

## HELPER FUNCTION ##
def change_mode(mode: str, tokens: list, voices: list, octave: int, mutation: str, voice: int) -> tuple:
    # get token and compare
    command = tokens[0].split("\\")[1].strip()

    # change mode
    if command == INSTRUCT: return (INSTRUCT, octave, mutation, voice)
    elif command == SCORE: return (SCORE, octave, mutation, voice)
    elif command == VOICE:
        voice += 1
        voices.append([])
        return (VOICE, octave, mutation, voice)
    elif command == OCTAVE: return (mode, int(tokens[1]), mutation, voice)
    elif command == MUTATION: return (mode, octave, str(tokens[1]), voice)
    
    # mode note found
    return (None, octave, mutation, voice)

def update_file_data(tokens: "list[str]", file_data: dict) -> None:
    key = tokens[0].rstrip(":")
    value = " ".join(tokens[1:]).strip()
    if key in file_data:
        file_data[key] = value

def update_voices(tokens:"list[str]", voice_data: "list[dict]", octave: int, mutation: str, duration: int, chords: list) -> int | list:
    # go through the notes
    for note in tokens:
        # check for the start of a chord
        if note.count("<") > 0:
            note = note.replace("<", "")
            chords.append("<")

        # check if note has beats and change the duration
        if re.search("[0-9]", note):
            # count dots & remove
            num_dots = note.count(".")
            if num_dots > 0: note = note.replace("." * num_dots, "")

            # get beat & remove
            duration = int(re.findall(r'\d+', note)[0])
            if duration > 0: note = note.replace(str(duration), "")

            # normalize duration
            duration = 1 / duration * 4

            # calculate beat
            for _ in range(num_dots):  duration += duration / 2

        if note not in NOTES:
            continue

        # create note and add to chords
        note_info = parse_note(note, duration, octave, mutation)
        chords.append(note_info)
        
        # skip if we are in the middle of a chord
        if chords[0] == "<" and note != ">":
            continue
        
        # remove special characters
        if chords[0] == "<": del chords[0]
        if chords[-1]["type"] == "note" and chords[-1]["note"] == ">": del chords[-1]

        # add chord to coice data and clear
        voice_data.append(chords.copy())
        chords.clear()

    return duration, chords

def parse_note(note: str, duration: float, octave: int, mutation: str) -> dict:
    # rest 
    if note == "-":
        return {"type": "rest", "duration": duration}
    # note
    return {"type": "note", "note": note, "duration": duration, "octave": octave, "mutation": mutation}


# x, y = process_file("modules/J'ai_mis__Je_n'en_puis__Puerorum.organum")
# x, y = process_file("modules/chords.organum")
x, y = process_file("modules/test.organum")
# print(x)
# print(y[2])
# for v, i in enumerate(y):
#     print(f"Voice #{v+1} (notes={len(i)})")
#     for j in i:
#         print(j)