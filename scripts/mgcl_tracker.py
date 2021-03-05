import os
import argparse
import textwrap
import re
import logging


class Tracker:
    def __init__(self, start_dir, lower, upper, exts):
        self.start_dir = start_dir
        self.lower = int(lower)
        self.upper = int(upper)
        self.exts = tuple(exts)

        self.accounted_for = {i: False for i in range(self.lower, self.upper + 1)}
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
            # print("error logged @ {}...".format(nums[0]))
            logging.error("Could not parse number in filename: {}".format(nums[0]))
        except Exception as e:
            # print("unknwon error occurred:", e)
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

        # print(
        #     " done!\n\n{} Found numbers written to".format(len(self.accounted_for)),
        #     os.path.abspath(os.path.join(self.start_dir, "tracker_found_numbers.txt")),
        # )

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
            os.path.abspath(os.path.join(self.start_dir, "tracker_found_numbers.txt")),
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

        # return len(self.accounted_for)


def cli():
    my_parser = argparse.ArgumentParser(
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

    my_parser.add_argument(
        "-d",
        "--start_dir",
        required=True,
        type=str,
        help="path to the starting directory",
    )

    my_parser.add_argument(
        "-l",
        "--lower",
        required=True,
        type=int,
        help="The lower bound MGCL number to include in count",
    )

    my_parser.add_argument(
        "-u",
        "--upper",
        required=True,
        type=int,
        help="The upper bound MGCL number to include in count",
    )

    my_parser.add_argument(
        "-e",
        "--exts",
        required=False,
        nargs="+",
        default=["png", "jpg", "jpeg"],
        help="The upper bound MGCL number to include in count (default is png jpg jpeg)",
    )

    args = my_parser.parse_args()

    start_dir = args.start_dir
    lower = args.lower
    upper = args.upper
    exts = args.exts

    print(
        "**WARNING: This script indexes all files recursively from the start. As a result, this can take an exceptional amount of time for large targets.**\n"
    )

    print("Program starting...\n")

    tracker = Tracker(start_dir, lower, upper, exts)
    # unique_occurrences = tracker.run()
    tracker.run()

    print("\nAll computations completed...")
    # print(
    #     "Found {} unique instances of MGCL numbers in range: {} <= num <= {}".format(
    #         unique_occurrences, int(lower), int(upper)
    #     )
    # )


if __name__ == "__main__":
    cli()
