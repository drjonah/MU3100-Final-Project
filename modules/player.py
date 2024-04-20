import numpy as np
import pyaudio
from file import process_file

## WAVEFORM GENERATION AND ALTERATIONS ##
def fade_waveform(waveform: np.float32) -> np.float32:
    """This takes a waveform and adds fades to make the note more fluid

    Args:
        waveform (np.float32): waveform for current note

    Returns:
        np.float32: this is the new waveform with fade applied
    """
    # fade length based on duration
    duration = 0.02
    fade_length = int(44100 * duration)

    # creates the fade length ; [start / stop] values
    fade_in = np.linspace(0, 1, fade_length)
    fade_out = np.linspace(1, 0, fade_length)

    # adds a fade to the beginning and end of the waveform
    waveform[:fade_length] *= fade_in
    waveform[-fade_length:] *= fade_out

    return waveform

def add_slur(waveform1: np.float32, waveform2: np.float32) -> np.float32:
    """This takes two waveforms and adds a slur by pitch translation

    Args:
        waveform1 (np.float32): this first waveform
        waveform2 (np.float32): this second waveform

    Returns:
        np.float32: this is the new waveform with fade applied
    """
    rate = 44100  # Sample rate
    transition_samples = int(rate * 0.02)  # Number of samples over which to transition

    # Create transition window
    transition_window = np.linspace(0, 1, transition_samples)

    # Fade out the end of the first waveform
    waveform1[-transition_samples:] *= (1 - transition_window)

    # Fade in the beginning of the second waveform
    waveform2[:transition_samples] *= transition_window

    # Concatenate the modified waveforms
    # Here we overlap the last part of waveform1 and the first part of waveform2
    combined_waveform = np.concatenate([waveform1[:-transition_samples], waveform1[-transition_samples:] + waveform2[:transition_samples], waveform2[transition_samples:]])

    return combined_waveform.astype(np.float32)

def mix_waveforms(waveforms: "list[np.ndarray]") -> np.ndarray:
    """This will take waveforms and overlay them so that they are a single waveform file

    Args:
        waveforms (list[np.ndarray]): this is the array of all waveform files

    Returns:
        np.ndarray: a single combined waveform
    """
    max_len = max(len(waveform) for waveform in waveforms) if len(waveforms) > 0 else len(waveforms)

    # array of zeros of the maximum length for the mixed audio
    mixed_audio = np.zeros(max_len, dtype=np.float32)

    # pad each waveform to the max length for safety and add it to the mixed_audio
    for waveform in waveforms:
        padded_waveform = np.pad(waveform, (0, max_len - len(waveform)), mode='constant')
        mixed_audio += padded_waveform

    # Scale down by the number of waveforms to keep average amplitude similar to the original
    return mixed_audio / len(waveforms)

def generate_sound_waveform(frequency: float, duration, volume=1) -> np.float32:
    """This generates a notes waveform based on frequency

    Args:
        frequency (float): frequncy for given note
        duration (float, optional): duration for the note.
        volume (int, optional): volume for the note. Defaults to 1.

    Returns:
       np.float32: this is the waveform for the note
    """
    t = np.linspace(0, duration, int(44100 * duration), endpoint=False)
    waveform = volume * np.sin(2 * np.pi * frequency * t)
    return waveform.astype(np.float32)

def generate_rest_waveform(duration) -> np.float32:
    """This generates a rest waveform based on frequency

    Args:
        duration (float, optional): duration for the rest. Defaults to 0.5.

    Returns:
       np.float32: this is the waveform for the rest
    """
    # Calculate the number of samples
    num_samples = int(44100 * duration)
    # Create an array of zeros
    silence_waveform = np.zeros(num_samples, dtype=np.float32)
    return silence_waveform

def generate_frequency(note: str, octave: int, mutation: int) -> float:
    """This generates the frequency for a note on a variety of factors

    Args:
        note (str): this is what hexachord note to play
        octave (int): this is how many octaves about the default hexachord octave
        mutation (int): this determines the frequency based on medival hexachord

    Returns:
        float: frequency for parameters
    """
    to_mutation = {
        "G": 98,
        "c": 130,
        "f": 174,
        "g": 196,
        "c'": 262,
        "f'": 349,
        "g'": 392
    }
    to_semitone = {
        "ut": 0,
        "re": 2,
        "me": 4,
        "fa": 5,
        "sol": 7,
        "la": 9
    }
    semitone = to_semitone[note] if note in to_semitone.keys() else to_semitone["ut"]
    hexachord = to_mutation[mutation] if mutation in to_mutation.keys() else to_mutation["c'"]

    # calculate and return frequency
    return (hexachord) * (2**(semitone/12)) * (2**octave)

def music_to_waveform(music: "list[dict]") -> np.ndarray:
    """This is the main function to translate music notation to a single waveform

    Args:
        music (list[dict]): array of musical notes stored as dictionaries

    Returns:
        np.ndarray: returned waveform
    """
    # note array for all the note waveforms
    voice = []
    # keeps record for joined waveforms
    current_waveform = None
    # convert music to waveform
    for note in music:
        # handle note
        if note["type"] == "note":
            
            # clean note
            join = note["note"].endswith("+") 
            music_note = note["note"].rstrip("+")

            # generate frequency and waveform
            frequency = generate_frequency(music_note, note["octave"], note["mutation"])
            waveform = generate_sound_waveform(frequency, note["duration"])

            # add to current
            if join and current_waveform is not None:
                current_waveform = add_slur(current_waveform, waveform)

            # join but none detected
            elif join:
                current_waveform = waveform

            else:
                # no join detected but previous exists to cross fade
                if current_waveform is not None:
                    current_waveform = add_slur(current_waveform, waveform)
                    current_waveform = fade_waveform(current_waveform)
                    # return
                    voice.append(current_waveform)
                    current_waveform = None
                # regular note
                else:
                    waveform = fade_waveform(waveform)
                    voice.append(waveform)

        # handle rest
        elif note["type"] == "rest":
            # generate rest waveform
            rest_waveform = generate_rest_waveform(note["duration"])
            # reset join because a rest cant be joined
            if current_waveform is not None:
                voice.append(current_waveform)
                current_waveform = None
            # add rest
            voice.append(rest_waveform)

    # check if last note was meant to be joined
    if current_waveform is not None:
        voice.append(current_waveform)

    # generate rest buffer
    voice.append(generate_rest_waveform(duration=1))

    # make one waveform
    return np.concatenate(voice)

## MAIN ##
def play(filepath: str):
    # pyaudio 
    print("preparing audio stream...")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)

    # prepare
    print("reading organum file...")
    file_data, organum = process_file(filepath)

    print("generating waveform...")
    organum = [music_to_waveform(voice) for voice in organum] # generate the waveforms for each voice

    print("mixing waveforms...")
    mixed_waveform = mix_waveforms(organum)

    print(f"playing \"{file_data["title"]}\" by {file_data["composer"]}...")
    stream.write(mixed_waveform.tobytes())

    print("done!")
    stream.close() # Clean up PyAudio and close streams
    p.terminate() # terminate pyaudio


# play("modules/test.organum")
play("modules/J'ai_mis__Je_n'en_puis__Puerorum.organum")