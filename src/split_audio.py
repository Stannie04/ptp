import os
import re

from tqdm import tqdm
from pydub import AudioSegment
from parse_txt import get_split_composition_files, count_notes, txt_to_string
from parse_alignments import alignments_from_csv
from constants import SPLIT_TXT_DIR, AUDIO_DIR, SPLIT_AUDIO_DIR

def get_split_times(alignments, piece, author, split_files):
    n_notes = [count_notes(txt_to_string(file, piece)) for file in split_files]
    current_note = 0

    # Sanity check
    if sum(n_notes) != len(alignments):
        print(f"ERROR ({author}_{piece}): The number of notes in the split files does not match the number of alignments. Ignoring.")
        print(f"Number of notes in split files: {sum(n_notes)}")
        print(f"Number of alignments: {len(alignments)}")
        return None

    splits = []
    for n in n_notes:
        start_split = alignments[current_note][0]
        if current_note + n >= len(alignments):
            end_split = alignments[len(alignments)-1][1]
            break
        else:
            end_split = alignments[current_note+n-1][1]
        splits.append((start_split, end_split))
        current_note += n
    return splits

def split_mp3(author, piece):
    """Split an mp3 file into segments based on the given splits."""

    split_files = get_split_composition_files(piece)
    alignments = alignments_from_csv(author, piece)
    splits = get_split_times(alignments, piece, author, split_files)
    audio_filename = f"{author}_{piece}"

    if splits is None:
        return

    if not os.path.exists(f"{SPLIT_AUDIO_DIR}/{author}/{piece}"):
        os.makedirs(f"{SPLIT_AUDIO_DIR}/{author}/{piece}")

    try: audio = AudioSegment.from_file(f"{AUDIO_DIR}/{author}/{audio_filename}.mp3")
    except: audio = AudioSegment.from_file(f"{AUDIO_DIR}/{author}/{audio_filename}.opus")

    for i, split in enumerate(splits):
        start, end = split
        start_frame = int(float(start)*1000)
        end_frame = int(float(end)*1000)

        segment = audio[start_frame:end_frame]
        segment.export(f"{SPLIT_AUDIO_DIR}/{author}/{piece}/{audio_filename}_{i}.wav", format="wav")


def pieces_by_author(author):
    files = os.listdir(f"{AUDIO_DIR}/{author}")
    audio_files = [f for f in files if re.search(r'\.(mp3|opus)$', f)]

    pieces = []
    for a in audio_files:
        full_name = a[len(author)+1:]
        pieces.append(full_name.split('.', 1)[0])
    return pieces

def main():
    all_pieces = os.listdir(SPLIT_TXT_DIR)
    authors = tqdm(os.listdir(AUDIO_DIR))
    for a in authors:
        pieces = pieces_by_author(a)
        for p in pieces:
            authors.set_description(f"Splitting {a} - {p}")
            if p in all_pieces:
                split_mp3(a, p)
            else:
                print(f"WARNING: The file {p} is not a recognized piece. Ignoring.")


if __name__ == "__main__":
    main()