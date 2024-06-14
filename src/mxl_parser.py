import os
import sys
import json
import music21
from constants import MXL_DIR, NOTE_DICT, SPLIT_TXT_DIR, SPLIT_AUDIO_DIR, NOTE_NAMES
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
    note_seq = f"{NOTE_NAMES[note.pitch.name]}{note.pitch.octave}{NOTE_DICT[note.duration.type]}{dots}"
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

def remove_last_measure(seq):
    for i, el in enumerate(seq[::-1]):
        if el == ']' or el == ':':
            return seq[:-i]
    return seq

def mxl_to_seq(score_name, score, measure_split):
    full_seq = []
    seq = []
    score = score.chordify()
    score_list = list(score.recurse())
    bpm = None
    seen_measures = []

    with open('alt_endings.json', 'r') as file:
        alt_endings = json.load(file)

    for i, el in enumerate(score_list):
        if isinstance(el, music21.bar.Repeat):
            if el.direction == 'end':
                full_seq.extend(seq)
                full_seq.extend(seq)
                seq = []
            elif el.direction == 'start':
                full_seq.extend(seq)
                seq = []

        if isinstance(el, music21.stream.Measure):
            if el.number in seen_measures and el.number in alt_endings.get(score_name, []):
                full_seq = remove_last_measure(full_seq)
            seen_measures.append(el.number)

            if el.number % measure_split == 0:
                seq.append(':')
                if bpm:
                    seq.append(f"{bpm}")
            else:
                seq.append(']')

        elif isinstance(el, music21.chord.Chord):
            seq.append(parse_chord(el, score_list, i))

        elif isinstance(el, music21.tempo.MetronomeMark):
            bpm = str(el.number)
            if bpm == "None":
                bpm = str(el.numberSounding)
            seq.append(bpm)

    full_seq.extend(seq)

    """
    Remove first measure marker.
    This needs to be done here and not initially, as potential repeats need the first measure marker to properly copy the sequence.
    """
    return ' '.join(full_seq[1:])

def split_seq_and_write(composition, seq):
    """Write each split sequence (a given number of bars) to a separate text file."""

    segments = seq.split(':')
    for i, segment in enumerate(segments):
        with open(f"{SPLIT_TXT_DIR}/{composition[:-4]}_{i+1}.txt", 'w') as file:
            file.write(segment.strip())
            file.close()

def parse_mxl(measure_split=1):
        compositions = tqdm(os.listdir(MXL_DIR))
        for c in compositions:
            compositions.set_description(f"Processing {c}")
            mxl_file = music21.converter.parse(f'{MXL_DIR}/{c}')
            seq = mxl_to_seq(c, mxl_file, int(measure_split))
            split_seq_and_write(c, seq)


def measure_at_offset(score, offset):
    """Return the measure number at a given offset."""

    measure_num = 0
    for m in score.parts[0].getElementsByClass('Measure'):
        if m.offset <= offset:
            measure_num += 1
    return measure_num

def double_notes(c):
    """Check wheter the same notes is played by multiple parts at a given time."""

    score = music21.converter.parse(f'{MXL_DIR}/{c}')
    notes = score.flatten().notesAndRests
    notes_at_offset = {}
    for i, n in enumerate(notes):
        if not n.isRest:
            if isinstance(n, music21.chord.Chord):
                for note in n:
                    if note.offset not in notes_at_offset:
                        notes_at_offset[note.offset] = []
                    if note.pitch.nameWithOctave in notes_at_offset[note.offset]:
                        print(f"Double chord note in {c} at measure {measure_at_offset(score, n.offset)}: {note.pitch.nameWithOctave}")
                    notes_at_offset[note.offset].append(note.pitch.nameWithOctave)
            else:
                if n.offset not in notes_at_offset:
                    notes_at_offset[n.offset] = []
                if n.pitch.nameWithOctave in notes_at_offset[n.offset]:
                    print(f"Double note in {c} at measure {measure_at_offset(score, n.offset)}: {n.pitch.nameWithOctave}")
                notes_at_offset[n.offset].append(n.pitch.nameWithOctave)


def main():
    if len(sys.argv) != 1:
        mxl_file = music21.converter.parse(f'{MXL_DIR}/{sys.argv[1]}')
        seq = mxl_to_seq(mxl_file, 3)
        print(seq)
        print(f"Successfully parsed {sys.argv[1]}.")
    else:
        parse_mxl()
        # compositions = tqdm(os.listdir(MXL_DIR))
        # for c in compositions:
        #     double_notes(c)

if __name__ == "__main__":
    main()