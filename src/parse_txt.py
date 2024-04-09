import os
import re

from constants import SPLIT_TXT_DIR

def count_notes(seq):
    """Count the number of notes in a sequence, excluding rests."""

    return len(re.findall(r'[A-G]', seq))

def txt_to_string(file, piece):
    """Read a txt file and return its contents as a string."""

    with open(f"{SPLIT_TXT_DIR}/{piece}/{file}") as f:
        return f.read()

def get_split_composition_files(score_name):
    """Return the split txt files corresponding to the given filename."""

    file_list = os.listdir(f"{SPLIT_TXT_DIR}/{score_name}")
    return sorted(file_list, key=lambda x: int(x.split('_')[-1].split('.')[0]))

def main():
    txt_files = os.listdir(SPLIT_TXT_DIR)
    for file in txt_files:
        split_txt_files = os.listdir(f"{SPLIT_TXT_DIR}/{file}")
        for f in split_txt_files:
                seq = txt_to_string(f"{SPLIT_TXT_DIR}/{file}", f)
                n_notes = count_notes(seq)
                print(f"{f}: {n_notes}")


if __name__ == "__main__":
    main()