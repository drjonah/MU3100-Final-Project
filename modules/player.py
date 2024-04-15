import numpy as np
import pyaudio
import threading
import matplotlib.pyplot as plt
# from modules.voice import Voice

## STREAM FUNCTIONS ##
def play(waveform: np.float32, start_event: threading.Event, stream: pyaudio.Stream) -> None:
    """This takes a waveform and plays it when the start event is triggered

    Args:
        waveform (np.float32): waveform for current note
        start_event (threading.Event): threading event
        stream (pyaudio.Stream): stream for pyaudio
    """
    # Wait for the threading event to start.
    # This happens after each voice is initialized
    start_event.wait()

    # Play waveform
    stream.write(waveform.tobytes())
    
def setup_stream(p: pyaudio.PyAudio) -> pyaudio.Stream:
    """This sets up PyAudio stream and returns the stream object

    Returns:
        pyaudio.Stream: PyAudio stream object
    """
    return p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)

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
    transition_samples = int(rate * 0.05)  # Number of samples over which to transition

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

def generate_sound_waveform(frequency: float, duration=0.5, volume=1) -> np.float32:
    """This generates a notes waveform based on frequency

    Args:
        frequency (float): frequncy for given note
        duration (float, optional): duration for the note. Defaults to 0.5.
        volume (int, optional): volume for the note. Defaults to 1.

    Returns:
       np.float32: this is the waveform for the note
    """
    t = np.linspace(0, duration, int(44100 * duration), endpoint=False)
    waveform = volume * np.sin(2 * np.pi * frequency * t)
    return waveform.astype(np.float32)

def generate_rest_waveform(duration=0.5) -> np.float32:
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

def generate_frequency(note: int, octave: int, mutation: int) -> float:
    """This generates the frequency for a note on a variety of factors

    Args:
        note (int): this is what hexachord note to play
        octave (int): this is how many octaves about the default hexachord octave
        mutation (int): this determines the frequency based on medival hexachord

    Returns:
        float: frequency for parameters
    """
    #                     G   c    f    g    c'   f'   g'
    # c' is equal to middle c
    # in hz
    hexachord_frequency = [98, 130, 174, 196, 262, 349, 392]
    note_to_semitone = {
        0: 0,
        1: 2,
        2: 4,
        3: 5,
        4: 7,
        5: 9
    }

    semitone = note_to_semitone[note]
    mutation += 4

    #            starting frequency                change semi tone      change octave
    frequency = (hexachord_frequency[mutation]) * (2**(semitone/12)) * (2**octave)

    return frequency

def generate_music(music: "list[dict]") -> np.ndarray:
    """This is the main function to translate music notation to a single waveform

    Args:
        music (list[dict]): array of musical notes stored as dictionaries

    Returns:
        np.ndarray: returned waveform
    """
    # note array for all the note waveforms
    notes = []
    # keeps record for joined waveforms
    current_waveform = None
    # convert music to waveform
    for note in music:
        # handle note
        if note["type"] == "note":
            # generate frequency and waveform
            frequency = generate_frequency(note["note"], note["octave"], note["mutation"])
            waveform = generate_sound_waveform(frequency, duration=1)

            # add to current
            if note["join"] == True and current_waveform is not None:
                current_waveform = add_slur(current_waveform, waveform)

            # join but none detected
            elif note["join"] == True:
                current_waveform = waveform

            else:
                # no join detected but previous exists to cross fade
                if current_waveform is not None:
                    current_waveform = add_slur(current_waveform, waveform)
                    current_waveform = fade_waveform(current_waveform)
                    # return
                    notes.append(current_waveform)
                    current_waveform = None
                # regular note
                else:
                    waveform = fade_waveform(waveform)
                    notes.append(waveform)

        # handle rest
        elif note["type"] == "rest":
            # generate rest waveform
            rest_waveform = generate_rest_waveform()
            # reset join because a rest cant be joined
            if current_waveform is not None:
                notes.append(current_waveform)
                current_waveform = None
            # add rest
            notes.append(rest_waveform)

    # check if last note was meant to be joined
    if current_waveform is not None:
        notes.append(current_waveform)

    # generate rest buffer
    notes.append(generate_rest_waveform(duration=1))

    # make one waveform
    return np.concatenate(notes)

## MAIN ##
def main():
    # pyaudio 
    p = pyaudio.PyAudio()

    # voices
    # voice1 = [
    #     {"type": "note", "note": 0, "octave": 0, "join": True},
    #     {"type": "note", "note": 1, "octave": 0, "join": False},
    #     {"type": "note", "note": 2, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": True},
    #     {"type": "note", "note": 5, "octave": 0, "join": True},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": True},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "rest"},

    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 1, "octave": 0, "join": False},
    #     {"type": "note", "note": 2, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": True},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 5, "octave": 0, "join": True},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": True},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},

    # ]
    # voice2 = [
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},

    #     {"type": "note", "note": 1, "octave": 0, "join": False},
    #     {"type": "note", "note": 1, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": False},
    #     {"type": "note", "note": 3, "octave": 0, "join": False},
    #     {"type": "note", "note": 4, "octave": 0, "join": False},
    #     {"type": "note", "note": 2, "octave": 0, "join": True},
    #     {"type": "note", "note": 1, "octave": 0, "join": False},
    #     {"type": "note", "note": 0, "octave": 0, "join": True},
    #     {"type": "note", "note": 1, "octave": 0, "join": False},
    # ]

    voice1 = [
        {"type": "note", "note": 0, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 1, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 2, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 3, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 4, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 5, "octave": 0, "mutation": 0, "join": True},

        {"type": "note", "note": 0, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 1, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 2, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 3, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 4, "octave": 0, "mutation": 0, "join": True},
        {"type": "note", "note": 5, "octave": 0, "mutation": 0, "join": True},
    ]

    voice2 = [
        {"type": "rest"},
        {"type": "rest"},
        {"type": "rest"},
        {"type": "rest"},
        {"type": "note", "note": 4, "octave": 0, "mutation": 1, "join": True},
        {"type": "note", "note": 5, "octave": 0, "mutation": 1, "join": True},
        
        {"type": "note", "note": 0, "octave": 0, "mutation": 1, "join": True},
        {"type": "note", "note": 1, "octave": 0, "mutation": 1, "join": True},
        {"type": "note", "note": 2, "octave": 0, "mutation": 1, "join": True},
        {"type": "note", "note": 3, "octave": 0, "mutation": 1, "join": True},
        {"type": "note", "note": 4, "octave": 0, "mutation": 1, "join": True},
        {"type": "note", "note": 5, "octave": 0, "mutation": 1, "join": True},
    ]

    # prepare
    organum = [voice1, voice2]
    num_organum = len(organum)
    organum = [generate_music(voice) for voice in organum]
    streams = [setup_stream(p) for _ in range(num_organum)]

    # Create a threading event
    start_event = threading.Event()

    # Create threads
    threads = []
    for i in range(num_organum):
        t = threading.Thread(target=play, args=(organum[i], start_event, streams[i]))
        t.start()
        threads.append(t)

    # Trigger start
    start_event.set()

    # Wait for both threads to complete
    for thread in threads:
        thread.join()
    # Clean up PyAudio and close streams
    for stream in streams:
        stream.close()
    # terminate pyaudio
    p.terminate()

if __name__ == "__main__":
    main()