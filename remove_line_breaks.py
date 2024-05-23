import re
from collections import Counter
import argparse


def find_most_common_length_range(line_lengths, range_size):
    filtered_lengths = [length for length in line_lengths if length >= 3]
    length_counter = Counter(filtered_lengths)
    max_count = 0
    best_range = (0, 0)

    for length in length_counter:
        current_count = sum(length_counter[length + offset]
                            for offset in range(-range_size, range_size + 1))
        if current_count > max_count:
            max_count = current_count
            best_range = (length - range_size, length + range_size)

    return best_range


def remove_unwanted_line_breaks(text, range_size=1, end_punctuation=r'[。.!?，,；;：“”‘’""\'\'（）()]'):
    lines = text.split('\n')

    lines = [line.strip() for line in lines if line]

    line_lengths = [len(line) for line in lines]

    best_range = find_most_common_length_range(line_lengths, range_size)

    print(f'Most common line length range: {best_range}')

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Remove unwanted line breaks in text.')
    parser.add_argument('input', type=str, help='Input text file')
    parser.add_argument('output', type=str, help='Output text file')
    parser.add_argument('--range-size', type=int, default=1,
                        help='Size of the range to find most common line length')
    parser.add_argument('--end-punctuation', type=str, default='[。.!?，,；;：“”‘’""\'\'（）()]',
                        help='Regex pattern for punctuation that indicates the end of a line')

    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()

    cleaned_text = remove_unwanted_line_breaks(
        text, args.range_size, args.end_punctuation)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
