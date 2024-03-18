import defusedxml
defusedxml.defuse_stdlib() # XML security issues patch

import os
import muspy
from tqdm import tqdm

def duration_per_timestep(mxl_file):
    """Calculate the duration of a single timestep in ptp format.

    Given time measure (n,d) and the timesteps per measure (tpm), this formula is given by:
    t_dur = n*(4/d)/tpm.
    """

    time_signature = (mxl_file.time_signatures[0].numerator, mxl_file.time_signatures[0].denominator)
    tpm = mxl_file.barlines[1].time # timesteps per measure, Assuming no measure changes for now
    return time_signature[0] * (4/time_signature[1]) / tpm


def mxl_to_seq(mxl_file):
    """Convert a given mxl file to a ptp string of notes."""

    seq = []
    t_playing = 0 # Timesteps remaining until no notes are playing
    t_rest = 0 # Timesteps a rest has been playing
    notes = mxl_file.tracks[0].notes
    t_dur = duration_per_timestep(mxl_file)

    for t in tqdm(range(notes[0].time, notes[len(notes)-1].time + 1)):
        current_notes = [note for note in notes if note.time == t]
        if current_notes:
            if t_rest > 0:
                seq.append(f"_/{t_rest * t_dur}")
                t_rest = 0
            chord = []
            for note in current_notes:
                t_playing = max(t_playing, note.duration)
                chord.append(f'{note.pitch_str}/{note.duration * t_dur}')
            seq.append(f"{','.join(chord)}")

        else:
            if t_playing <= 0:
                t_rest = t_rest + 1
        t_playing = t_playing - 1

    return f"{' '.join(seq)}"


def main():
    data_path = "data"
    compositions = os.listdir(data_path)
    # compositions = ["Rachmaninoff_-_Piano_Concerto_No._2_Op._18"]
    for c in compositions:
        print(f"Parsing {c}")
        mxl_file = muspy.read(f'{data_path}/{c}/{c}.mxl')
        parsed = mxl_to_seq(mxl_file)
        with open(f'{data_path}/{c}/{c}.txt', 'w') as file:
            file.write(parsed)
        file.close()

if __name__ == "__main__":
    main()