import os
import sys
import music21
from constants import MXL_DIR, NOTE_DICT, SPLIT_TXT_DIR, SPLIT_AUDIO_DIR
from tqdm import tqdm

def handle_tie(note, score, i):
    remaining_list = score[i:]
    for el in remaining_list:
        if isinstance(el, music21.chord.Chord):
            for n in el:
                if n.tie and n.pitch == note.pitch:
                    dots = ">" * n.duration.dots
                    if n.tie.type == "stop":
                        return f"{NOTE_DICT[n.duration.type]}{dots}"

def parse_note(note, score, i):
    dots = ">" * note.duration.dots
    note_seq = f"{note.pitch}{NOTE_DICT[note.duration.type]}{dots}"
    if note.tie:
        if note.tie.type == "start":
            add = handle_tie(note, score, i)
            if add:
                return f"{note_seq}{add}"
            return f"{note_seq}"
        return ""
    return note_seq

def parse_chord(chord, score, i):
    chord_seq = []

    if chord.isRest:
        dots = ">" * chord.duration.dots
        return f"_{NOTE_DICT[chord.duration.type]}{dots}"

    for note in chord:
        note_seq = parse_note(note, score, i)
        if note_seq:
            chord_seq.append(note_seq)
    return ",".join(chord_seq)

def mxl_to_seq(score, measure_split):
    seq = []
    first = True
    score = score.chordify()
    score_list = list(score.recurse())
    for i, el in enumerate(score_list):
        if isinstance(el, music21.stream.Measure):
            if el.number % measure_split == 0:
                if first:
                    first = False
                else:
                    seq.append(f':{bpm}')
            else:
                seq.append(']')
        elif isinstance(el, music21.chord.Chord):
            seq.append(parse_chord(el, score_list, i))
        elif isinstance(el, music21.tempo.MetronomeMark):
            bpm = str(el.number)
            if bpm == "None":
                bpm = str(el.numberSounding)
            seq.append(bpm)
    return ' '.join(seq)

def split_seq_and_write(composition, seq):
    """Write each split sequence (a given number of bars) to a separate text file."""

    segments = seq.split(':')
    for i, segment in enumerate(segments):
        with open(f"{SPLIT_TXT_DIR}/{composition[:-4]}_{i}.txt", 'w') as file:
            file.write(segment.strip())
            file.close()

def parse_mxl(measure_split=3):
        compositions = tqdm(os.listdir(MXL_DIR))
        for c in compositions:
            compositions.set_description(f"Processing {c}")
            mxl_file = music21.converter.parse(f'{MXL_DIR}/{c}')
            seq = mxl_to_seq(mxl_file, int(measure_split))
            split_seq_and_write(c, seq)


def main():
    if len(sys.argv) != 1:
        mxl_file = music21.converter.parse(f'{MXL_DIR}/{sys.argv[1]}')
        # mxl_file.show('text')
        seq = mxl_to_seq(mxl_file, 3)
        # split_seq_and_write(sys.argv[1], seq)
        print(seq)
        print(f"Successfully parsed {sys.argv[1]}.")
    else:
        parse_mxl()

if __name__ == "__main__":
    main()