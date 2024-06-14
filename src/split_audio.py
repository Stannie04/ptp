import os
import sys
import re

from tqdm import tqdm
from pydub import AudioSegment
from txt_parser import get_split_composition_files, count_notes, txt_to_string
from alignments_parser import alignments_from_csv
from constants import AUDIO_DIR, SPLIT_AUDIO_DIR, ALIGNMENT_DIR

def get_split_times(alignments, n_notes):
    current_note = 0

    splits = []
    for n in n_notes:
        start_split = alignments[current_note][0]
        if current_note + n >= len(alignments):
            end_split = alignments[len(alignments)-1][1]
            splits.append((start_split, end_split))
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
    n_notes = [count_notes(txt_to_string(file)) for file in split_files]

    # Sanity check
    if sum(n_notes) != len(alignments):
        print(f"ERROR ({author}_{piece}): The number of notes in the split files does not match the number of alignments.")
        print(f"Number of notes in split files: {sum(n_notes)}, {n_notes}")
        print(f"Number of alignments: {len(alignments)}")

    splits = get_split_times(alignments, n_notes)
    audio_filename = f"{author}_{piece}"

    if splits is None:
        return

    try: audio = AudioSegment.from_file(f"{AUDIO_DIR}/{author}/{audio_filename}.mp3")
    except: audio = AudioSegment.from_file(f"{AUDIO_DIR}/{author}/{audio_filename}.opus")

    audio = audio.set_frame_rate(22050)

    for i, split in enumerate(splits):
        start, end = split
        start_frame = int(float(start)*1000) # Convert to ms
        end_frame = int(float(end)*1000)

        segment = audio[start_frame:end_frame]
        segment.export(f"{SPLIT_AUDIO_DIR}/{audio_filename}_{i+1}.wav", format="wav", parameters=["-ac", "1"])


def pieces_by_author(author):
    files = os.listdir(f"{AUDIO_DIR}/{author}")
    audio_files = [f for f in files if re.search(r'\.(mp3|opus)$', f)]

    pieces = []
    for a in audio_files:
        full_name = a[len(author)+1:]
        pieces.append(full_name.split('.', 1)[0])
    return pieces

def split_all():
    authors = tqdm(os.listdir(AUDIO_DIR))
    for a in authors:
        pieces = pieces_by_author(a)
        for p in pieces:
            authors.set_description(f"Splitting {a} - {p}")
            split_mp3(a, p)

def split_full_to_mvt(author, full_piece):

    full_filename = f"{author}_{full_piece}"

    author_alignments = os.listdir(f"{ALIGNMENT_DIR}/{author}")
    piece_alignments = sorted([a for a in author_alignments if a.startswith(full_filename)])

    try: audio = AudioSegment.from_file(f"{AUDIO_DIR}/{author}/{full_filename}.mp3")
    except: audio = AudioSegment.from_file(f"{AUDIO_DIR}/{author}/{full_filename}.opus")

    audio = audio.set_frame_rate(22050)

    for i,p in enumerate(piece_alignments):
        mvt_alignments = alignments_from_csv(author, p[len(author)+1:-4])
        end_split = mvt_alignments[-1][1]
        end_frame = int(float(end_split)*1000)

        segment = audio[:end_frame]
        segment.export(f"{AUDIO_DIR}/{author}/{full_filename}_mov{i+1}.mp3", format="mp3", parameters=["-ac", "1"])
        audio = audio[end_frame:]

def main():
    if len(sys.argv) == 3:
        split_full_to_mvt(sys.argv[1], sys.argv[2])
        return
    else:
        split_all()
    return


if __name__ == "__main__":
    main()