import os
import re

from constants import SPLIT_TXT_DIR

def count_notes(seq):
    """Count the number of notes in a sequence, excluding rests."""
    return len(re.findall(r'[A-G]', seq))

def txt_to_string(path, file):
    """Read a txt file and return its contents as a string."""

    with open(f"{path}/{file}") as f:
        return f.read()

def get_split_composition_files(file):
    """Return the split txt files corresponding to the given filename.

    @TODO: Numerically sort split files
    """

    split_txt_files = os.listdir(SPLIT_TXT_DIR)
    regex = r'{}_[0-9]+\.txt'.format(file[:-4])
    name_length = len(file[:-4])+1 # plus 1 for the underscore
    split_files = [f for f in split_txt_files if re.match(regex, f)]
    return split_files

def main():
    split_txt_files = os.listdir(SPLIT_TXT_DIR)
    for f in split_txt_files:
        seq = txt_to_string(SPLIT_TXT_DIR, f)
        n_notes = count_notes(seq)
        print(f"{f}: {n_notes}")


if __name__ == "__main__":
    main()