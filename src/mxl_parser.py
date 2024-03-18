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
    tpm = mxl_file.barlines[2].time - mxl_file.barlines[1].time # timesteps per measure accounting for "opmaat", Assuming no measure changes for now
    return time_signature[0] * (4/time_signature[1]) / tpm


def get_current_notes(notes, t, prev_index):
    """Get all notes that are playing at a given timestep t.

    Notes are assumed to be sorted by time, so prev_index is used to avoid iterating through the entire list.
    """

    current_notes = []
    for i in range(prev_index, len(notes)):
        if notes[i].time == t:
            current_notes.append(notes[i])
        else:
            return current_notes, i
    return current_notes, len(notes)


def handle_barline(bar_index, seq, mxl_file, t):
    """Add a barline to the sequence if the current timestep is a barline.

    @TODO: Fix rests over multiple bars.
    @TODO: Segment a certain number of measures for processing later on.
    """

    if t == mxl_file.barlines[bar_index].time:
        seq.append("|")
        return bar_index + 1
    return bar_index


def parse_chord(current_notes, t_dur, t_playing, t_rest, seq):
    """Convert the notes played at to a ptp string.

    If applicable, add a rest to the sequence.
    """

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

    return t_playing-1, t_rest


def mxl_to_seq(mxl_file):
    """Convert a given mxl file to a ptp string of notes."""

    seq = []
    prev_index, t_playing, t_rest = 0, 0, 0
    bar_index = 1 # Skip first barline
    notes = mxl_file.tracks[0].notes
    t_dur = duration_per_timestep(mxl_file)

    for t in tqdm(range(notes[len(notes)-1].time + 1)):
        bar_index = handle_barline(bar_index, seq, mxl_file, t)
        current_notes, prev_index = get_current_notes(notes, t, prev_index)
        t_playing, t_rest = parse_chord(current_notes, t_dur, t_playing, t_rest, seq)

    return f"{' '.join(seq)}"


def main():
    data_path = "data"
    compositions = os.listdir(data_path)
    for c in compositions:
        print(f"Parsing {c}")
        mxl_file = muspy.read(f'{data_path}/{c}/{c}.mxl')
        parsed = mxl_to_seq(mxl_file)
        with open(f'{data_path}/{c}/{c}.txt', 'w') as file:
            file.write(parsed)
        file.close()

if __name__ == "__main__":
    main()