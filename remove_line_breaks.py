import re
from collections import Counter
import argparse
import os
from tqdm import tqdm
import chardet
from multiprocessing import Pool, cpu_count
import logging
from datetime import datetime

# Configure logging
log_filename = datetime.now().strftime("log_%Y-%m-%d.log")
logging.basicConfig(
    filename=log_filename,
    filemode='a',  # Append to the log file
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Set the logging level to INFO
)


def find_most_common_length_range(line_lengths, range_size, frequency_threshold):
    filtered_lengths = [length for length in line_lengths if length >= 3]
    length_counter = Counter(filtered_lengths)
    max_count = 0
    best_range = (0, 0)

    total_lines = len(filtered_lengths)

    for length in length_counter:
        current_count = sum(length_counter[length + offset]
                            for offset in range(-range_size, range_size + 1))
        current_frequency = current_count / total_lines
        if current_frequency >= frequency_threshold and current_count > max_count:
            max_count = current_count
            best_range = (length - range_size, length + range_size)

    return best_range


def remove_unwanted_line_breaks(text, range_size=1, frequency_threshold=0.1, end_punctuation=r'[。.!?，,；;：“”‘’""\'\'（）()]', file_name=''):
    lines = text.split('\n')

    lines = [line.strip() for line in lines if line]

    line_lengths = [len(line) for line in lines]

    best_range = find_most_common_length_range(
        line_lengths, range_size, frequency_threshold)

    if best_range == (0, 0):
        logging.warning(
            f"{file_name}: No suitable line length range found based on the given frequency threshold.")
        return text

    logging.info(
        f"{file_name}: Most common line length range: {best_range}")

    merged_lines = []
    buffer = ""
    previous_line = ""

    for line in lines:
        if len(previous_line) in range(best_range[0], best_range[1] + 1) and (not previous_line or not re.search(end_punctuation, previous_line[-1])):
            buffer += line
        else:
            if buffer:
                merged_lines.append(buffer)
            buffer = line

        previous_line = line

    if buffer:
        merged_lines.append(buffer)

    return '\n'.join(merged_lines)


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']


def process_file(args):
    input_file, output_file, range_size, frequency_threshold, end_punctuation = args
    encoding = detect_encoding(input_file)
    with open(input_file, 'r', encoding=encoding, errors='ignore') as f:
        text = f.read()

    cleaned_text = remove_unwanted_line_breaks(
        text, range_size, frequency_threshold, end_punctuation, os.path.basename(input_file))

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

    logging.info(f'Processed file: {input_file} -> {output_file}')


def process_folder(input_folder, output_folder, range_size, frequency_threshold, end_punctuation):
    tasks = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.txt'):
                input_file = os.path.join(root, file)
                relative_path = os.path.relpath(input_file, input_folder)
                output_file = os.path.join(output_folder, relative_path)
                tasks.append((input_file, output_file, range_size,
                             frequency_threshold, end_punctuation))

    with Pool(cpu_count()) as pool:
        list(tqdm(pool.imap(process_file, tasks), total=len(tasks), ncols=80))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Remove unwanted line breaks in text files within a folder.')
    parser.add_argument('input_folder', type=str,
                        help='Input folder containing text files')
    parser.add_argument('output_folder', type=str,
                        help='Output folder to save cleaned text files')
    parser.add_argument('--range-size', type=int, default=1,
                        help='Size of the range to find most common line length')
    parser.add_argument('--frequency-threshold', type=float, default=0.5,
                        help='Minimum frequency threshold for the line length range')
    parser.add_argument('--end-punctuation', type=str, default='[。.!?，,；;：“”‘’""\'\'（）()]',
                        help='Regex pattern for punctuation that indicates the end of a line')

    args = parser.parse_args()

    process_folder(args.input_folder, args.output_folder,
                   args.range_size, args.frequency_threshold, args.end_punctuation)
