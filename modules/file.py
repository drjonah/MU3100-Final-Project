import logging
import pprint

# constants
INSTRUCT, SCORE, VOICE, OCTAVE, MUTATION, BEATS = "instruct", "score", "voice", "octave", "mutation", "beats"
NOTES = ["ut", "re", "me", "fa", "sol", "la", "ut+", "re+", "me+", "fa+", "sol+", "la+", "-"]

## MAIN FUNCTION ##
def process_file(filepath: str) -> dict | list:
    voices = []
    file_data = {"title": None, "composer": None, "letter": None}

    mode = None
    octave = None
    mutation = None
    beats = None
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
                mode, octave, mutation, beats, voice = change_mode(mode, tokens, voices, octave, mutation, beats, voice)
                # error detected
                if mode == None: 
                    logging.error("mode not found")
                continue
            
            # process mode
            if mode == INSTRUCT:
                update_file_data(tokens, file_data)
            elif mode == VOICE:
                update_voices(tokens, voices[voice], octave, mutation, beats)

    return file_data, voices

## HELPER FUNCTION ##
def change_mode(mode: str, tokens: list, voices: list, octave: int, mutation: str, beats: int, voice: int) -> tuple:
    # get token and compare
    command = tokens[0].split("\\")[1].strip()

    # change mode
    if command == INSTRUCT: return (INSTRUCT, octave, mutation, beats, voice)
    elif command == SCORE: return (SCORE, octave, mutation, beats, voice)
    elif command == VOICE:
        voice += 1
        voices.append([])
        return (VOICE, octave, mutation, 1, voice)
    elif command == OCTAVE: return (mode, int(tokens[1]), mutation, beats, voice)
    elif command == MUTATION: return (mode, octave, str(tokens[1]), beats, voice)
    elif command == BEATS: return (mode, octave, mutation, str(tokens[1]), voice)
    
    # mode note found
    return (None, octave, mutation, beats, voice)

def update_file_data(tokens: "list[str]", file_data: dict) -> None:
    key = tokens[0].rstrip(":")
    value = " ".join(tokens[1:]).strip()
    if key in file_data:
        file_data[key] = value

def update_voices(tokens:"list[str]", voice_data: "list[dict]", octave: int, mutation: str, beats: str) -> None:
    # find dot
    num_dots = beats.count("*")
    if num_dots > 0:
        beats = beats[:beats.find("*")]

    # fraction or whole
    if beats.find("/") >= 0:
        try:
            n, d = beats.split("/")
            duration = float(n) / float(d) * 4
        except:
            logging.error(f"improper beat length for voice with notes {(" ").join(tokens)}")
            duration = 1
    else: duration = float(beats)

    # add dots
    for _ in range(num_dots):
        duration += duration / 2

    for note in tokens:
        if note not in NOTES:
            continue
        note_info = parse_note(note, duration, octave, mutation)
        voice_data.append(note_info)

def parse_note(note: str, duration: float, octave: int, mutation: str) -> dict:
    # rest 
    if note == "-":
        return {"type": "rest", "duration": duration}
    # note
    return {"type": "note", "note": note, "duration": duration, "octave": octave, "mutation": mutation}


# x, y = process_file("modules/J'ai_mis__Je_n'en_puis__Puerorum.organum")

# pprint.pprint(y)