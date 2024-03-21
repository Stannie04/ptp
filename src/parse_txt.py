import os
import re

def count_notes(seq):
    regex = r'(?<!_)\/' # All occurences of / without an underscore (rest) before
    notes = re.findall(regex, seq)
    return len(notes)

def txt_to_string(txt_dir, file):
    with open(f"{txt_dir}/{file}") as f:
            seq = f.read()
            f.close()
    return seq

def main():
    txt_dir = "data/split_txt"
    # txt_dir = "data/whole_scores"
    txt_files = os.listdir(txt_dir)
    for f in txt_files:
        seq = txt_to_string(txt_dir, f)
        n_notes = count_notes(seq)
        print(f"{f}: {n_notes}")


if __name__ == "__main__":
    main()