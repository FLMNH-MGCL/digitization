import os
import sys
import argparse
import textwrap
import re
import pandas as pd
from pathlib import Path, PureWindowsPath
from Helpers import Helpers


def error_message(message):
    print("dynaiello.py: error:", message)
    sys.exit(1)


# its like Aiello, but a little more dynamic (hence, dynaiello)
class Dynaiello:
    def __init__(self, start_dir, destination, excel_file, csv_file):
        self.start_dir = start_dir
        self.destination = destination
        self.mgcl_nums = dict()

        if excel_file is None:
            self.csv_file = csv_file
            self.raw_data = Dynaiello.parse_file(self.csv_file, True)
        else:
            self.excel_file = excel_file
            self.raw_data = Dynaiello.parse_file(self.excel_file, False)

        rename_headers = self.raw_data.columns.value

        # We are going to manually extract the catalogNumber during search for rename,
        # every other header will just be appended automatically. Therefore, I am removing
        # the catalogNumber here so it is not duplicated
        self.rename_pieces = filter(lambda header: header !=
                                    "catalogNumber", rename_headers)

    @staticmethod
    def check_valid_sources(filepath, ext):
        # check file existence
        if not os.path.exists(filepath):
            error_message("provided file does not exist in the fs")

        # check if file is actually a file
        if os.path.exists(filepath) and not os.path.isfile(filepath):
            error_message(
                "provided file is not of the correct type (i.e. it is not a file)")

        # check file extension
        # TODO: update to use pathlib
        file_vec = os.path.basename(filepath).split(".")
        if len(file_vec) < 2:
            error_message("provided file is missing a valid extension")

        passed_ext = file_vec[1]

        if ext != passed_ext.lower():
            error_message(
                "passed extension {} must match either csv or xlsx".format(passed_ext))

        return True

    @staticmethod
    def parse_file(file_path, is_csv):
        """
        Attempts to parse CSV or Excel data of specimen

        :param file_path: The os path str to the CSV file
        :type file_path: str

        :param is_csv: whether or not file is a CSV
        :type is_csv: bool

        :return: DataFrame
        """
        ext = "csv" if is_csv else "xlsx"

        Dynaiello.check_valid_sources(file_path, ext)

        raw_data = None

        if is_csv:
            raw_data = pd.read_csv(file_path)
        else:
            raw_data = pd.read_excel(file_path)

        return raw_data

    def collect_files(self):
        """
        Collects all image files, not marked as duplicates at and below the starting directory

        :rtype: list of str representing paths to images in fs
        """
        return list(dict((str(f), f.stat().st_size) for f in Path(self.start_dir).glob('**/*') if (f.is_file() and "duplicate" not in str(f) and Helpers.valid_image(str(f)))).keys())

    def generate_name(self, found, item, catalogNumber):
        ext = found.split('.')[1]
        viewarr = found.split('_')
        view = viewarr[len(viewarr) - 1]

        new_name = catalogNumber

        for piece in self.rename_pieces:
            new_name += "_{}".format(item[piece])

        new_name += '_{}.{}'.format(view, ext)

        return new_name

    def handle_items(self, item, filtered_list):
        for find in filtered_list:
            if "downscale" in find:
                print("skipping duplicate image:", find)

            catalogNumber = item['catalogNumber'].strip()

            new_name = self.generate_name(find, item, catalogNumber)

            if os.path.exists(os.path.join(self.destination, new_name)):
                print("skipping file:", find,
                      'as its generated name', new_name, 'already exists in destination')
            else:
                print('copying and moving file to destination:',
                      find, 'to', new_name)

            if self.mgcl_nums[catalogNumber]:
                self.mgcl_nums[catalogNumber] = self.mgcl_nums[catalogNumber].append(
                    (find, new_name))
            else:
                self.mgcl_nums[catalogNumber] = [].append(find)

    def run(self):
        files = self.collect_files()

        # df.loc[df['column_name'] == some_value]
        for _id, item in self.raw_data.iterrows():
            filtered_list = filter(
                lambda fi: item['catalogNumber'].strip() in fi, files)

            if len(filtered_list > 0):
                self.handle_items(item, filtered_list)


def cli():
    my_parser = argparse.ArgumentParser(description="Dynaiello is a version of the Aiello script with less column restrictions. Copy and rename entries based on a CSV file.",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
          Example Runs:
            python3 ./dynaiello.py --start_dir /fake/path --csv_file /path/to/file.csv\n
            python3 ./dynaiello.py --start_dir /fake/path --excel_file /path/to/file.xlsx
         '''))

    my_parser.add_argument('-s', '--start_dir', required=True,
                           type=str, help="path to the starting directory")
    my_parser.add_argument('-d', '--destination', required=True,
                           type=str, help="path to the destination directory")

    group_files = my_parser.add_mutually_exclusive_group(required=True)
    group_files.add_argument(
        '-f', '--csv_file', action='store', help="path to CSV of specimen data")
    group_files.add_argument(
        '-e', '--excel_file', action='store', help="path to XLSX of specimen data")

    args = my_parser.parse_args()

    print("Program starting...\n")
    # wrangler.run()
    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()
