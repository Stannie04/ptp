import os
import sys
from tqdm import tqdm
from txt_parser import get_split_composition_files, count_notes, txt_to_string, get_chord_sequence
from alignments_parser import alignments_from_csv
from split_audio import pieces_by_author
from constants import MXL_DIR, AUDIO_DIR


def get_full_mxl_len():
    full_scores = os.listdir(MXL_DIR)
    score_names = sorted([f.split('.')[0] for f in full_scores])
    for score in score_names:
        split_files = get_split_composition_files(score)
        n_notes = [count_notes(txt_to_string(file)) for file in split_files]
        print(f"{score}: {sum(n_notes)}")

def get_author_length():
    authors = os.listdir(AUDIO_DIR)
    for a in authors:
        pieces = pieces_by_author(a)
        for p in pieces:
            alignments = alignments_from_csv(a, p)
            print(f"{a}_{p}: {len(alignments)}")

def note_nr_from_alignment(author, piece, split_nr, verbose=False):
    """Given a split filename, return the number of the starting note in the full alignment."""

    split_files = get_split_composition_files(piece)
    n_notes = [count_notes(txt_to_string(file)) for file in split_files]
    if verbose:
        print(f"{author}_{piece}_{split_nr} starts at line {sum(n_notes[:split_nr])+2}.")
    return sum(n_notes[:split_nr])

def find_alignment_errors(author, piece):

    split_files = get_split_composition_files(piece)
    txt_split_files = [txt_to_string(file) for file in split_files]
    alignments = alignments_from_csv(author, piece)

    i = 0
    for enum, txt in enumerate(txt_split_files):
        chord_seq = get_chord_sequence(txt)
        for ch in chord_seq:
            if not (alignments[i+ch-1][0] == alignments[i][0] and not alignments[i][0] == alignments[i+ch][0]):
                print(f"Error at split {enum} (measure {enum+1}) note {i - note_nr_from_alignment(author, piece, enum, verbose=False) + 1} (line {i+2}): Expected chord of length {ch}.")
                return
            i += ch

def chord_start_errors(author, piece):
    """Prints the split number and line number of the first note of each chord that does not start at the beginning of a split."""

    offset = 0
    split_files = get_split_composition_files(piece)
    start_notes = [note_nr_from_alignment(author, piece, i) for i in range(len(split_files))]
    alignments = alignments_from_csv(author, piece)
    for enum, _ in enumerate(split_files):
        if start_notes[enum] == 0: continue
        if alignments[start_notes[enum]+offset][0] == alignments[start_notes[enum]-1+offset][0]:
            print(f"Chord in split {enum} (line {start_notes[enum]+2}) does not start at the beginning of the split.")
            offset += 1

def main():
    if len(sys.argv) == 1:
        get_full_mxl_len()
        get_author_length()
    if len(sys.argv) == 3:
        # find_alignment_errors(sys.argv[1], sys.argv[2])
        chord_start_errors(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 4:
        note_nr_from_alignment(sys.argv[1], sys.argv[2], int(sys.argv[3]), verbose=True)

if __name__ == "__main__":
    main()