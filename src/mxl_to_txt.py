import defusedxml
defusedxml.defuse_stdlib() # XML security issues patch

import os
import sys
import music21
from tqdm import tqdm

from constants import MXL_DIR, NOTE_DICT, SPLIT_TXT_DIR

def parse_chord(chord):
    """Convert a chord to a ptp string.

    @TODO: Handle complex durations.
    """

    chord_seq = []

    if chord.isRest:
        dots = ">" * chord.duration.dots
        if chord.duration.type == "complex":
            return f"_COMPLEX{dots}"
        return f"_{NOTE_DICT[chord.duration.type]}{dots}"

    for note in chord:
        dots = ">" * note.duration.dots
        note_seq = f"{note.pitches[0]}{NOTE_DICT[note.duration.type]}{dots}"
        chord_seq.append(note_seq)
    return ",".join(chord_seq)

def mxl_to_seq(mxl_file):
    """Convert a given mxl file to a ptp string of notes."""

    seq = []
    chordified_mxl = mxl_file.chordify()
    chords = chordified_mxl.flatten().notesAndRests
    print(chords)
    time_signature = mxl_file.getTimeSignatures()[0]
    quarters_per_measure = time_signature.numerator * 4 / time_signature.denominator
    total_duration = 0
    measure_count = 0

    for chord in chords:
        total_duration += chord.duration.quarterLength
        if total_duration > quarters_per_measure:
            measure_count += 1
            if measure_count % 3 == 0:
                seq.append(":")
            else:
                seq.append("|")
            total_duration = total_duration % quarters_per_measure
        seq.append(parse_chord(chord))
    return " ".join(seq)

def split_seq_and_write(composition, seq):
    """Write each split sequence (a given number of bars) to a separate text file."""

    if not os.path.exists(f"{SPLIT_TXT_DIR}/{composition[:-4]}"):
        os.makedirs(f"{SPLIT_TXT_DIR}/{composition[:-4]}")

    segments = seq.split(':')
    for i, segment in enumerate(segments):
        with open(f"{SPLIT_TXT_DIR}/{composition[:-4]}/{composition[:-4]}_{i}.txt", 'w') as file:
            file.write(segment.strip())
            file.close()

def main():
    if len(sys.argv) != 1:
        try:
            mxl_file = music21.converter.parse(f'{MXL_DIR}/{sys.argv[1]}')
            seq = mxl_to_seq(mxl_file)
            split_seq_and_write(sys.argv[1], seq)
            print(f"Successfully parsed {sys.argv[1]}.")
        except:
            print(f"ERROR: Could not parse {sys.argv[1]}.")
    else:
        compositions = tqdm(os.listdir(MXL_DIR))
        for c in compositions:
            compositions.set_description(f"Parsing {c}")
            mxl_file = music21.converter.parse(f'{MXL_DIR}/{c}')
            seq = mxl_to_seq(mxl_file)
            split_seq_and_write(c, seq)

if __name__ == "__main__":
    main()