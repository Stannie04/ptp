import os
import sys
import music21
from constants import MXL_DIR, NOTE_DICT, SPLIT_TXT_DIR
from tqdm import tqdm

#TODO: cleanup long sequences (e.g. C5exxxxxoesttstsxxss>tttttssttst -> C5q)
def handle_tie(note):
    next_note = note
    while True:
        if next_note == None:
            return ""
        next_note = next_note.next()
        if isinstance(next_note, music21.note.Note):
            if next_note.pitch == note.pitch:
                return parse_note(next_note, tied=True)

def parse_note(note, tied=False):
    dots = ">" * note.duration.dots

    if tied:
        if note.tie and note.tie.type == "stop":
            return f"{NOTE_DICT[note.duration.type]}{dots}"
        return f"{NOTE_DICT[note.duration.type]}{dots}{handle_tie(note)}"


    note_seq = f"{note.pitches[0]}{NOTE_DICT[note.duration.type]}{dots}"

    if note.tie:
        if note.tie.type == "start":
            note_seq += handle_tie(note)
        else:
            return ""
    return note_seq

def parse_chord(chord):
    """Convert a chord to a ptp string."""

    chord_seq = []

    if chord.isRest:
        dots = ">" * chord.duration.dots
        return f"_{NOTE_DICT[chord.duration.type]}{dots}"

    for note in chord:
        note_seq = parse_note(note, tied=False)
        if note_seq:
            chord_seq.append(note_seq)
    return ",".join(chord_seq)

def mxl_to_seq(score):
    score = score.chordify()
    seq = []
    for measure in score.getElementsByClass('Measure'):
        for chord in measure.flatten().getElementsByClass('Chord'):
            chord_seq = parse_chord(chord)
            if chord_seq:
                seq.append(chord_seq)
        if measure.number % 3 == 0:
            seq.append(":")
        else:
            seq.append("|")
    return " ".join(seq)

def split_seq_and_write(composition, seq):
    """Write each split sequence (a given number of bars) to a separate text file."""

    segments = seq.split(':')
    for i, segment in enumerate(segments):
        with open(f"{SPLIT_TXT_DIR}/{composition[:-4]}_{i}.txt", 'w') as file:
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