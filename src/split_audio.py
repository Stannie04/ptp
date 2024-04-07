import os
import re
from pydub import AudioSegment
from parse_txt import get_split_composition_files, count_notes, txt_to_string
from constants import ALIGNMENT_DIR, SPLIT_TXT_DIR, AUDIO_DIR, SPLIT_AUDIO_DIR

def alignments_from_csv(author, piece):
    """Return a list of alignments from a CSV file."""
    alignments = []
    with open(f"{ALIGNMENT_DIR}/{author}/{author}_{piece}.csv", 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                alignments.append(line.split(','))
    return alignments[1:]


def get_split_times(alignments, piece, author, split_files):
    n_notes = [count_notes(txt_to_string(file, piece)) for file in split_files]
    current_note = 0

    # Sanity check
    if sum(n_notes) != len(alignments):
        print(f"WARNING: The number of notes in the split files does not match the number of alignments.")
        print(f"Number of notes in split files: {sum(n_notes)}")
        print(f"Number of alignments: {len(alignments)}")
        print(f"{author} - {piece}")

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
    print(len(alignments))
    splits = get_split_times(alignments, piece, author, split_files)
    audio_filename = f"{author}_{piece}"

    if not os.path.exists(f"{SPLIT_AUDIO_DIR}/{author}/{piece}"):
        os.makedirs(f"{SPLIT_AUDIO_DIR}/{author}/{piece}")

    audio = AudioSegment.from_mp3(f"{AUDIO_DIR}/{author}/{audio_filename}.mp3")
    for i, split in enumerate(splits):
        start, end = split
        start_frame = int(float(start)*1000)
        end_frame = int(float(end)*1000)

        segment = audio[start_frame:end_frame]
        segment.export(f"{SPLIT_AUDIO_DIR}/{author}/{piece}/{audio_filename}_{i}.wav", format="wav")

def combine_mov_alignments(author, piece):
    """Combine the csv files of the movements into a single csv file.

    The time is counted up from the beginning of the piece.
    """

    all_alignments = os.listdir(f"{ALIGNMENT_DIR}/{author}")
    mov_alignments = [f for f in all_alignments if re.search(f"{author}_{piece}_mov\d.csv", f)]
    if not mov_alignments:
        print(f"WARNING: No alignment files found for {author} - {piece}.")
        return

    final_note = 0
    combined_alignments = [("start", "end")]
    for mov in mov_alignments:
        alignments = alignments_from_csv(author, f"{piece}_mov{mov[-5]}")
        for a in alignments[1:]:
            start = float(a[0]) + final_note
            end = float(a[1]) + final_note
            combined_alignments.append((start, end))
        final_note += float(alignments[-1][1])

def pieces_by_author(author):
    files = os.listdir(f"{AUDIO_DIR}/{author}")
    audio_files = [f for f in files if re.search(r'\.mp3$', f)] # @TODO: .opus
    return [a[len(author)+1:-4] for a in audio_files] # remove everything until the underscore and the file extension

def main():
    all_pieces = os.listdir(SPLIT_TXT_DIR)
    authors = os.listdir(AUDIO_DIR)
    for a in authors:
        pieces = pieces_by_author(a)
        for p in pieces:
            if p in all_pieces:
                split_mp3(a, p)
            else:
                print(f"WARNING: The file {p} is not a  recognized piece. Ignoring.")


if __name__ == "__main__":
    main()