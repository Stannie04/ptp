from pydub import AudioSegment
from parse_txt import get_split_composition_files, count_notes, txt_to_string
from constants import MXL_DIR, SPLIT_TXT_DIR, WAV_DIR

def alignments_from_csv(csv_file):
    """Return a list of alignments from a CSV file."""
    alignments = []
    with open(csv_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                alignments.append(line.split(','))
    return alignments[1:]

def split_mp3(mp3_file, splits):
    """Split an mp3 file into segments based on the given splits."""
    audio = AudioSegment.from_mp3(mp3_file)
    for i, split in enumerate(splits):
        start, end = split

        start = int(float(start)*1000)
        end = int(float(end)*1000)

        segment = audio[start:end]
        segment.export(f"{WAV_DIR}/wav_split/split_{i}.wav", format="wav")

def get_split_times(alignments, split_files):
    n_notes = [count_notes(txt_to_string(SPLIT_TXT_DIR, file)) for file in split_files]
    current_note = 0

    splits = []
    for n in n_notes:
        start_split = alignments[current_note][0]
        if current_note + n >= len(alignments):
            end_split = alignments[-1][1]
        else:
            end_split = alignments[current_note+n][1]
        splits.append((start_split, end_split))
        current_note += n
    return splits

def main():
    alignments = alignments_from_csv("oliver-colbentson_bwv1006_mov1.csv")
    split_files = get_split_composition_files("bwv1006_mov1.mxl")
    splits = get_split_times(alignments, sorted(split_files))
    split_mp3(f"{WAV_DIR}/wav_whole/oliver-colbentson_bwv1006_mov1.mp3", splits)


if __name__ == "__main__":
    main()