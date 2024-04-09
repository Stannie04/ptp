import os
import sys
import re
from constants import ALIGNMENT_DIR

def alignments_from_csv(author, piece):
    """Return a list of alignments from a CSV file."""

    alignments = []
    with open(f"{ALIGNMENT_DIR}/{author}/{author}_{piece}.csv", 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                alignments.append(line.split(','))
    return alignments[1:]

def merge_alignments_of_author(author, piece):
    """Combine all alignments of different movements of a single piece into one continous alignment list."""

    all_alignments = os.listdir(f"{ALIGNMENT_DIR}/{author}")
    mov_alignments = sorted([f for f in all_alignments if re.search(f"{author}_{piece}_mov\d.csv", f)])
    if not mov_alignments:
        print(f"WARNING: No alignment files found for {author} - {piece}.")
        return

    final_note = 0
    combined_alignments = [("start", "end")]
    for mov in mov_alignments:
        alignments = alignments_from_csv(author, f"{piece}_mov{mov[-5]}")
        for a in alignments:
            start = float(a[0]) + final_note
            end = float(a[1]) + final_note
            combined_alignments.append((start, end))
        final_note += round(float(alignments[-1][1]), 3)

    with open(f"{ALIGNMENT_DIR}/{author}/{author}_{piece}.csv", 'w') as file:
        for a in combined_alignments:
            file.write(f"{a[0]},{a[1]}\n")
        file.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python src/parse_alignments.py <author> <piece>")
        return
    merge_alignments_of_author(sys.argv[1], sys.argv[2])
    print(f"Successfully merged alignments for {sys.argv[1]} - {sys.argv[2]}.")

if __name__ == "__main__":
    main()