import os
import sys
import argparse
import textwrap
import re
import logging
from pathlib import Path
import pandas as pd


def error_message(message):
    print("mgcl_tracker.py: error:", message)
    sys.exit(1)


class Tracker:
    def __init__(self, start_dir, _range, nums, exts):
        self.start_dir = start_dir

        self.lower = int(_range[0]) if _range is not None else None
        self.upper = int(_range[1]) if _range is not None else None

        self.exts = tuple(exts)

        # if nums exists, accounted_for will be assigned to it, otherwise I generate it from the
        # range values
        self.accounted_for = {
            i: False for i in range(self.lower, self.upper + 1)} if nums is None else nums

        self.missing = dict()

        logging.basicConfig(
            level=logging.NOTSET,
            filename=os.path.join(start_dir, "tracker.log"),
            filemode="w",
            format="%(levelname)s - %(message)s",
        )

    def extract_number(self, file):
        regex = re.compile(r"(?:MGCL_)(\d*)(?:.*)")
        return regex.findall(file)

    def check_file(self, file):
        nums = self.extract_number(file)

        if not nums or len(nums) > 1:
            logging.error(
                "Unexpected file naming scheme @ {}: expected single number, recieved: {}".format(
                    file, nums
                )
            )
            return

        try:
            num = int(nums[0])

            if num < self.lower or num > self.upper:
                logging.debug("{} in {} not in range...".format(num, file))
                return
            elif num not in self.accounted_for:
                logging.error(
                    "unexpected error: number {} extracted from {} is not in dictionary but is somehow in range...".format(
                        num, file
                    )
                )
                return
            elif not self.accounted_for[num]:
                logging.debug("{} in {} is in range...".format(num, file))
                self.accounted_for[num] = True
        except ValueError:
            logging.error(
                "Could not parse number in filename: {}".format(nums[0]))
        except Exception as e:
            logging.error("unknwon error occurred: {}".format(e))

    def write_missing(self):
        print(
            "Logging numbers that could not be located (this may take time)...", end=""
        )

        with open(
            os.path.join(self.start_dir, "tracker_missing_numbers.txt"), "w"
        ) as f:
            for num, _ in self.missing.items():
                f.write("{}\n".format(num))

        print(" done!")

    def write_found(self):
        print(
            "Logging numbers that were located (this may take time)...",
            end="",
        )

        with open(os.path.join(self.start_dir, "tracker_found_numbers.txt"), "w") as f:
            for num, _ in self.accounted_for.items():
                f.write("{}\n".format(num))

        print(" done!\n")

    def write_out(self):
        self.write_missing()
        self.write_found()

        print(
            len(self.missing),
            "missing numbers total, written to",
            os.path.abspath(
                os.path.join(self.start_dir, "tracker_missing_numbers.txt")
            ),
            end="\n\n",
        )

        print(
            len(self.accounted_for),
            "found numbers total, written to",
            os.path.abspath(os.path.join(
                self.start_dir, "tracker_found_numbers.txt")),
        )

    def run(self):
        print("Starting os walk...", end="")
        for p, d, f in os.walk(self.start_dir):
            for file in f:
                if file.endswith(self.exts):
                    self.check_file(file)
        print(" done!\n")

        print("All files handled...\n")

        self.missing = dict(
            filter(lambda el: el[1] == False, self.accounted_for.items())
        )

        self.accounted_for = dict(
            filter(lambda el: el[1] == True, self.accounted_for.items())
        )

        self.write_out()


def extract_number(file):
    regex = re.compile(r"(?:MGCL_)(\d*)(?:.*)")

    nums = regex.findall(file)

    if not nums or len(nums) > 1:
        error_message(
            "unexpected cataglogNumber naming scheme @ {}: expected single number, recieved: {}".format(
                file, nums
            )
        )

    else:
        try:
            return int(nums[0])
        except ValueError:
            error_message(
                "Could not parse number in cataglogNumber: {}".format(nums[0]))
        except Exception:
            error_message(
                "Unknown error occurred when attempting to parse {}".format(nums[0]))


def parse_csv(csv_file):
    path_obj = Path(csv_file)

    ext = path_obj.suffix

    if ext is None:
        error_message("input_file missing extension")

    ext = ext.replace(".", "")

    if ext.lower() != "csv" and ext.lower() != "xlsx":
        error_message(
            "input_file extension {} must match either csv or xlsx (ignoring case)".format(
                ext
            )
        )

    raw_data = None

    if ext.lower() == "csv":
        raw_data = pd.read_csv(csv_file)
    elif ext.lower() == "xlsx":
        raw_data = pd.read_excel(csv_file)
    else:
        error_message(
            "Invalid file provided: expected .csv or .xlsx, recieved {}".format(ext.lower()))

    try:
        # this is a long complicated line so I will break it down
        # I create lambda to take an array of MGCL numbers and convert it to a dict { mgcl_number : bool }
        # I zip the raw data and an array of False values together and convert it to a dict
        # I call the lambda using the dataframe column 'catalogNumber' and convert to an array, and call extract number on
        # each element to grab JUST the number from the MGCL_#### pattern
        # I return the result of the invoked lambda function
        return (lambda raw_data: dict(zip(raw_data, [False for _ in range(len(raw_data))])))(
            [extract_number(i) for i in raw_data['catalogNumber'].tolist()]
        )
    except Exception:
        error_message(
            'Invalid formatting in .csv/.xlsx file: expected column \'catalogNumber\'')


def cli():
    parser = argparse.ArgumentParser(
        description="Track the used MGCL numbers in the filesystem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
          Example Runs:
            python3 ./mgcl_tracker.py --start_dir /fake/path --lower 1234567 --upper 2000000 \n
            python3 ./mgcl_tracker.py --start_dir /fake/path --lower 1234567 --upper 2000000 --exts png jpg
         """
        ),
    )

    parser.add_argument(
        "-d",
        "--start_dir",
        required=True,
        type=str,
        help="path to the starting directory",
    )

    parser.add_argument(
        "-e",
        "--exts",
        required=False,
        nargs="+",
        default=["png", "jpg", "jpeg"],
        help="The upper bound MGCL number to include in count (default is png jpg jpeg)",
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-r",
        "--range",
        nargs=2,
        help="The lower and upper bound MGCL numbers"
    )

    group.add_argument(
        '-f',
        '--file',
        help="A CSV of MGCL Numbers to search for"
    )

    args = parser.parse_args()

    start_dir = args.start_dir
    csv_file = args.file
    _range = args.range
    exts = args.exts

    nums = parse_csv(csv_file) if csv_file is not None else None

    print(
        "**WARNING: This script indexes all files recursively from the start. As a result, this can take an exceptional amount of time for large targets.**\n"
    )

    print("Program starting...\n")

    tracker = Tracker(start_dir, _range, nums, exts)
    tracker.run()

    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()
