import os
import sys
import argparse
import textwrap
import re
from datetime import datetime
import pandas as pd
from pathlib import Path
from Helpers import Helpers


def error_message(message):
    print("suspect_numbers.py: error:", message)
    sys.exit(1)


# TODO: add CSV parsing


class Suspector:
    def __init__(self, start_dir="", ranges=None, range_csv=None):
        self.start_dir = start_dir
        self.ranges = ranges
        self.range_csv = range_csv
        self.suspects = []

    @staticmethod
    def check_valid_sources(filepath, ext):
        file_vec = os.path.basename(filepath).split(".")
        if len(file_vec) < 2:
            error_message("provided file is missing a valid extension")

        passed_ext = file_vec[1]

        if ext != passed_ext.lower():
            error_message(
                "passed extension {} must match either csv or xlsx".format(passed_ext)
            )

        return True

    @staticmethod
    def parse_csv(file_path, is_csv):
        """
        Attempts to parse CSV data of bounding ranges

        :param file_path: The os path str to the CSV file
        :type file_path: str

        :return: an array of str, ordered list of lower,upper bound pairs
        :rtype: str[]
        """
        ext = "csv" if is_csv else "xlsx"
        Suspector.check_valid_sources(file_path, ext)

        raw_data = None
        ranges = []

        if is_csv:
            raw_data = pd.read_csv(file_path)
        else:
            raw_data = pd.read_excel(file_path)

        for _, row in raw_data.iterrows():
            try:
                lower = str(row["lower"])
                upper = str(row["upper"])

                ranges.append(lower)
                ranges.append(upper)
            except:
                error_message(
                    "missing either 'lower' or 'upper' bounds column in file. please run --help command to see supported structure for file inputs"
                )

        return ranges

    @staticmethod
    def validate_range(lower, upper):
        """
        Determines if lower is less than upper and inversely if upper is greater than lower.

        :param lower: The lower bound of the tuple range
        :type lower: unsigned integer

        :param upper: The upper bound of the tuple range
        :type upper: unsigned integer

        :rtype: bool
        """
        if lower >= upper or upper <= lower:
            return False

        return True

    @staticmethod
    def construct_ranges(ranges):
        """
        Constructs tuple array of 'ranges' from list of strings

        :param ranges: an array of str, ordered list of lower,upper bound pairs
        :type ranges: str[]

        :return: tuple array of ints representing a list of ranges, marked by lower and upper bounds
        :rtype: (int,int)[]
        """
        tuple_ranges = []

        for i in range(0, len(ranges), 2):
            lower = ranges[i]
            upper = ranges[i + 1]

            if (len(lower) < 6 or len(lower) > 8) or (len(upper) < 6 or len(upper) > 8):
                error_message(
                    "invalid ranges provided. Bounds must be between 6 and 8 digits"
                )

            try:
                lower = int(ranges[i])
                upper = int(ranges[i + 1])
            except:
                error_message(
                    "invalid ranges provided. Could not convert {} or {} to an integer type.".format(
                        lower, upper
                    )
                )

            if not Suspector.validate_range(lower, upper):
                error_message("invalid bounds in range {} - {}".format(lower, upper))

            tuple_ranges.append(tuple((lower, upper)))

        return tuple_ranges

    def collect_files(self):
        """
        Collects all image files, not marked as duplicates at and below the starting directory

        :rtype: list of str representing paths to images in fs
        """
        return list(
            dict(
                (str(f), f.stat().st_size)
                for f in Path(self.start_dir).glob("**/*")
                if (
                    f.is_file()
                    and "duplicate" not in str(f)
                    and Helpers.valid_image(str(f))
                )
            ).keys()
        )

    def is_in_ranges(self, collected_number):
        """
        Determines if number is withing any of the forbidden ranges

        :param collected_number: The number inside the image filename
        :type collected_number: int

        :return: whether or not collected_number is in any of the ranges
        :rtype: bool
        """
        for lower, upper in self.ranges:
            if collected_number <= upper and collected_number >= lower:
                return True

        return False

    def print_lineup(self):
        """
        lineup... get it? suspects? lineup? tough crowd... well, it just prints the 'suspects' found
        """
        now = datetime.now()
        timestamp = "{}_{}_{}-{}:{}".format(
            now.year, now.month, now.day, now.hour, now.minute
        )
        log_path = os.path.join(
            self.start_dir, "SUSPECTOR_LOG_{}.csv".format(timestamp)
        )

        print("\nPrinting suspect line-up...")

        with open(log_path, "w") as log:
            log.write("suspects\n")
            for suspect in self.suspects:
                log.write("{}\n".format(suspect))
                print(suspect)

    def run(self):
        """
        Main function for this utility class. Will collect files and perform all the checks.
        Any 'failing' files (i.e. in a forbidden range) will be added to 'self.suspects' to be
        logged before the return of this function
        """
        files = self.collect_files()

        for f in files:
            # note, I take the basename here to reduce the chance of a false positive in the event somewhere in the
            # file path there is a match before the file name itself
            matches = re.search(r"[0-9]{6,8}", os.path.basename(f))

            if matches is None:
                print("{}...".format(f), "failed! No regex match could be found!")
                print("Adding to list of suspects (as precaution)\n")
                self.suspects.append(f)
                continue

            invalid = True

            try:
                collected_number = int(matches.group(0))
                invalid = self.is_in_ranges(collected_number)
            except:
                print(
                    "{}...".format(f),
                    "failed! Something went wrong while handling file!",
                )
                print("Adding to list of suspects (as precaution)\n")
                self.suspects.append(f)
                continue

            if invalid:
                print("{}...".format(f), "failed! (seems sus to me)")
                print("Adding to list of suspects\n")
                self.suspects.append(f)

            else:
                print("{}...".format(f), "passed!")

        self.print_lineup()


# TODO: make me so I can import this file into other python scripts
def lib():
    pass


def cli():
    my_parser = argparse.ArgumentParser(
        description="Search through a filesystem at a given starting point and attempt to find any suspect numbers based on input",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
          CSV Format:
             lower,upper
             100000,100010
             200002,200030
             ...

          Example Runs:
            python3 ./suspect_numbers.py --start_dir /fake/path --ranges 1000 1003 2003 2030 2035 2042
            python3 ./suspect_numbers.py --start_dir /fake/path --csv_file /path/to/file.csv
         """
        ),
    )
    my_parser.add_argument(
        "-d",
        "--start_dir",
        required=True,
        type=str,
        help="path to the starting directory",
    )

    group = my_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-r",
        "--ranges",
        action="store",
        nargs="+",
        dest="ranges",
        help="List of ranges",
    )
    group.add_argument("-c", "--csv_file", action="store", help="path to CSV of ranges")
    group.add_argument(
        "-e", "--excel_file", action="store", help="path to excelsheet of ranges"
    )

    args = my_parser.parse_args()

    start_dir = args.start_dir
    ranges = args.ranges
    csv_file = args.csv_file
    excel_file = args.excel_file

    suspector = None

    if ranges != None and len(ranges) % 2 != 0:
        print(
            "usage: suspect_numbers.py [-h] -d START_DIR (-r RANGES [RANGES ...] | -f FILE_IN)"
        )
        error_message(
            "invalid range list provided, you must have both lower and upper bounds for each pair"
        )

    if ranges is None:
        if csv_file is not None:
            parsed_ranges = Suspector.parse_csv(csv_file, True)
            suspector = Suspector(
                start_dir, Suspector.construct_ranges(parsed_ranges), csv_file
            )
        else:
            parsed_ranges = Suspector.parse_csv(excel_file, False)
            suspector = Suspector(
                start_dir, Suspector.construct_ranges(parsed_ranges), csv_file
            )
    else:
        suspector = Suspector(start_dir, Suspector.construct_ranges(ranges))

    print("Program starting...\n")
    suspector.run()
    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()


"""
CLI TESTS

Failing Tests (they are supposed to fail)
=========================================
1). Invalid usage -> python3 ./suspect_numbers.py --start_dir /fake/path --ranges 1000 1003 2003 2030 2035 2042 --file /fake
2). Invalid range -> python3 ./suspect_numbers.py --start_dir /fake/path --ranges 1000 1003 2003 2030 2035
3). Invalid bounds in range -> python3 ./suspect_numbers.py --start_dir /fake/path --ranges 1000 1003 2003 2030 2035 2032

Testing Tests (who knows)
1). python3 ./suspect_numbers.py --start_dir /Users/aaronleopold/Documents/museum/flmnh/testing/MGCLChecker --ranges 1000 1003 2003 2030 2035 2042

"""
