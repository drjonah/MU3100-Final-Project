import logging, re

# constants
INSTRUCT, SCORE, VOICE, OCTAVE, MUTATION, BPM = "instruct", "score", "voice", "octave", "mutation", "bpm"
NOTES = ["ut", "re", "mi", "fa", "sol", "la", "ut+", "re+", "mi+", "fa+", "sol+", "la+", "-"]

## MAIN FUNCTION ##
def compile_score(filepath: str) -> dict | list:
    """This method will read a file by its path and return its data as dictionary and list."""
    voices = []
    file_data = {"title": None, "composer": None}

    mode = None
    octave = None
    mutation = None
    bpm = 120/60 # this is normalized
    chords = []
    duration = 1
    voice = -1
    start_chord = False
    end_chord = False

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
                mode, octave, mutation, bpm, voice = change_mode(mode, tokens, voices, octave, mutation, bpm, voice)
                # error detected
                if mode == None: 
                    logging.error("mode not found")
                continue
            
            # process mode
            if mode == INSTRUCT:
                update_file_data(tokens, file_data)
            elif mode == VOICE:
                duration, chords, start_chord, end_chord = update_voices(tokens, voices[voice], octave, mutation, bpm, duration, chords, start_chord, end_chord)

    return file_data, voices

## HELPER FUNCTION ##
def change_mode(mode: str, tokens: list, voices: list, octave: int, mutation: str, bpm: int, voice: int) -> tuple:
    """This method reads when a mode change occurs."""
    # get token and compare
    command = tokens[0].split("\\")[1].strip()

    # change mode
    if command == INSTRUCT: return (INSTRUCT, octave, mutation, bpm, voice)
    elif command == SCORE: return (SCORE, octave, mutation, bpm, voice)
    elif command == VOICE:
        voice += 1
        voices.append([])
        return (VOICE, octave, mutation, bpm, voice)
    elif command == OCTAVE: return (mode, int(tokens[1]), mutation, bpm, voice)
    elif command == MUTATION: return (mode, octave, str(tokens[1]), bpm, voice)
    elif command == BPM: return (mode, octave, mutation, int(tokens[1])/60, voice)
    
    # mode note found
    return (None, octave, mutation, bpm, voice)

def update_file_data(tokens: "list[str]", file_data: dict) -> None:
    """This method reads when to update the file's data."""
    key = tokens[0].rstrip(":")
    value = " ".join(tokens[1:]).strip()
    if key in file_data:
        file_data[key] = value

def update_voices(tokens:"list[str]", voice_data: "list[dict]", octave: int, mutation: str, bpm: int, duration: int, chords: list, start_chord: bool, end_chord: bool) -> int | list:
    """This method will transpose each note to readable notes for the player."""

    # go through the notes
    for note in tokens:
        # check for the start of a chord
        if note.count("<") > 0:
            note = note.replace("<", "")
            start_chord = True

        if note.count(">") > 0:
            note = note.replace(">", "")
            end_chord = True

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

            # take into account bpm
            duration /= bpm

            # calculate beat
            for _ in range(num_dots):  duration += duration / 2

        if note not in NOTES and not end_chord:
            continue

        # create note and add to chords
        if note:
            note_info = parse_note(note, duration, octave, mutation)
            chords.append(note_info)
        
        # skip if we are in the middle of a chord
        if start_chord and not end_chord:
            continue

        if chords[-1] == " ": del chords[-1]

        # add chord to voice data and clear
        voice_data.append(chords.copy())
        chords.clear()

        start_chord = False
        end_chord = False

    return duration, chords, start_chord, end_chord

def parse_note(note: str, duration: float, octave: int, mutation: str) -> dict:
    """This puts together a dictionary to house the transposed notes."""
    # rest 
    if note == "-":
        return {"type": "rest", "duration": duration}
    # note
    return {"type": "note", "note": note, "duration": duration, "octave": octave, "mutation": mutation}