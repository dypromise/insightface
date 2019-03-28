import os
import random
import argparse
import sys


class GeneratePairs:
    """
    Generate the pairs.txt file for applying validate on your own datasets.
    every ID dir's image should be named like: xxxx/xxxx_0000.jpg
    """

    def __init__(self, args):
        """
        Parameter data_dir, is your data directory.
        Parameter pairs_filepath, where is the pairs.txt that belongs to.
        Parameter img_ext, is the image data extension.
        """

        if not args.data_dir.endswith('/'):
            args.data_dir = args.data_dir + '/'

        if not args.saved_dir.endswith('/'):
            args.saved_dir = args.saved_dir + '/'

        self.data_dir = args.data_dir
        self.pairs_filepath = args.saved_dir + 'pairs.txt'
        self.repeat_times = int(args.repeat_times)
        self.img_ext = '.jpg'

    def generate(self):

        os.remove(self.pairs_filepath)

        for i in range(self.repeat_times):
            self._generate_matches_pairs()
            self._generate_mismatches_pairs()

    def get_folder_numbers(self):
        count = 0
        for folder in os.listdir(self.data_dir):
            if os.path.isdir(self.data_dir + folder):
                count += 1
        return count

    def _generate_matches_pairs(self):
        """
        Generate all matches pairs
        """
        matches_count = 0
        for name in os.listdir(self.data_dir):
            if matches_count >= 400:
                break

            if name == ".DS_Store" or name[-3:] == 'txt':
                continue

            a = []
            for file in os.listdir(self.data_dir + name):
                if file == ".DS_Store":
                    continue
                a.append(file)

            with open(self.pairs_filepath, "a") as f:
                # This line may vary depending on how your images are named.
                temp = random.choice(a).split("_")
                w = temp[0]
                l = random.choice(a).split("_")[1].lstrip(
                    "0").rstrip(self.img_ext)
                r = random.choice(a).split("_")[1].lstrip(
                    "0").rstrip(self.img_ext)
                if l == '' or r == '':
                    continue
                f.write(w + "\t" + l + "\t" + r + "\n")
                matches_count += 1

    def _generate_mismatches_pairs(self):
        """
        Generate all mismatches pairs
        """
        mismatches_count = 0
        for i, name in enumerate(os.listdir(self.data_dir)):
            if mismatches_count >= 400:
                continue

            if name == ".DS_Store" or name[-3:] == 'txt':
                continue

            remaining = os.listdir(self.data_dir)

            del remaining[i]
            remaining_remove_txt = remaining[:]
            for item in remaining:
                if item[-3:] == 'txt':
                    remaining_remove_txt.remove(item)

            remaining = remaining_remove_txt

            other_dir = random.choice(remaining)
            with open(self.pairs_filepath, "a") as f:
                if not os.path.isdir(self.data_dir + name) or \
                        not os.path.isdir(self.data_dir + other_dir):
                    continue

                if len(os.listdir(self.data_dir + name)) < 1 or \
                        len(os.listdir(self.data_dir + other_dir)) < 1:
                    continue

                file1 = random.choice(os.listdir(self.data_dir + name))
                file2 = random.choice(os.listdir(self.data_dir + other_dir))

                l = file1.split("_")[1].lstrip("0").rstrip(self.img_ext)
                r = file2.split("_")[1].lstrip("0").rstrip(self.img_ext)

                if l == '' or r == '':
                    continue

                f.write(name + "\t" + l + "\t" + other_dir + "\t" + r + "\n")
                mismatches_count += 1


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', type=str,
                        help='Directory with aligned images.')
    parser.add_argument('saved_dir', type=str, help='Directory to save pairs.')
    parser.add_argument('--repeat_times', type=str,
                        help='Repeat times to generate pairs', default=10)
    return parser.parse_args(argv)


if __name__ == '__main__':
    generatePairs = GeneratePairs(parse_arguments(sys.argv[1:]))
    generatePairs.generate()
