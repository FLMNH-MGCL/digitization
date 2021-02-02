import os
import sys
import argparse
import textwrap
import re
import pandas as pd
from pathlib import Path, PureWindowsPath


class Tracker:
    def __init__(self):
        pass

    def run(self):
        pass


def cli():
    my_parser = argparse.ArgumentParser(description="Track the used MGCL numbers in the filesystem",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
          Example Runs:
            python3 ./mgcl_tracker.py --start_dir /fake/path \n
            python3 ./mgcl_tracker.py --start_dir /fake/path 
         '''))

    my_parser.add_argument('-d', '--start_dir', required=True,
                           type=str, help="path to the starting directory")

    args = my_parser.parse_args()

    start_dir = args.start_dir

    print("Program starting...\n")

    # wrangler = Wrangler(start_dir, config, excel_file,
    #                     csv_file, sheet_id, sheet_url, worksheet)

    # wrangler.run()

    tracker = Tracker()

    tracker.run()
    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()
