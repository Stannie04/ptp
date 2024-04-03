import os
from parse_txt import get_split_composition_files, count_notes, txt_to_string
from constants import MXL_DIR, SPLIT_TXT_DIR


def main():
    compositions = os.listdir(MXL_DIR)
    for composition in compositions:
        split_files = get_split_composition_files(composition)
        for file in split_files:
            seq = txt_to_string(SPLIT_TXT_DIR, file)
            n_notes = count_notes(seq)
            print(f"{file}: {n_notes}")


if __name__ == "__main__":
    main()