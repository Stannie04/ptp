import os
import re

from constants import SPLIT_TXT_DIR

def count_notes(seq):
    """Count the number of notes in a sequence, excluding rests."""

    return len(re.findall(r'[A-G]', seq))

def txt_to_string(file):
    """Read a txt file and return its contents as a string."""
    with open(f"{SPLIT_TXT_DIR}/{file}") as f:
        return f.read()

def get_split_composition_files(score_name):
    """Return the split txt files corresponding to the given filename."""

    file_list = os.listdir(f"{SPLIT_TXT_DIR}")
    l = [f for f in file_list if re.match(f"{score_name}_\d+\.txt", f)]
    if not l:
        print(f"WARNING: No split files found for {l}")
    return sorted(l, key=lambda x: int(x.split('_')[-1].split('.')[0]))

def main():
    txt_files = os.listdir(SPLIT_TXT_DIR)
    print(len(txt_files))
    for file in txt_files:
        seq = txt_to_string(file)
        n_notes = count_notes(seq)
        print(f"{file}: {n_notes}")


if __name__ == "__main__":
    main()