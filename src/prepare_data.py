import os
import sys
from split_audio import split_all
from mxl_parser import parse_mxl
from txt_parser import txt_to_string
from constants import SPLIT_TXT_DIR, ALIGNMENT_DIR, SPLIT_AUDIO_DIR

def write_to_data():
    all_data = []
    authors = os.listdir(ALIGNMENT_DIR)
    split_files = os.listdir(f"{SPLIT_AUDIO_DIR}")
    for a in authors:
        name_len = len(a)+1 # +1 for the underscore
        for f in split_files:
            if f.startswith(a):
                txt_file = f"{f[name_len:-4]}.txt"
                seq = txt_to_string(txt_file)
                all_data.append((f, seq))

    with open("data.txt", 'w') as file:
        for data in all_data:
            file.write(f"data/{data[0]}|{data[1]}\n")
        file.close()

def empty_dirs():
    for d in [SPLIT_TXT_DIR, SPLIT_AUDIO_DIR]:
        for f in os.listdir(d):
            os.remove(f"{d}/{f}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python prepare_data.py <measures_per_split>")
        sys.exit(1)
    empty_dirs()
    parse_mxl(sys.argv[1])
    split_all()
    write_to_data()
    os.system("bash src/train_test_split.sh")

if __name__=="__main__":
    main()