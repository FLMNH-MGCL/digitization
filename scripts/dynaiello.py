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
    def __init__(self, start_dir, destination, input_file, views):
        self.start_dir = start_dir
        self.destination = destination
        self.views = views
        self.input_file = input_file
        self.mgcl_nums = dict()

        self.raw_data = Dynaiello.parse_file(self.input_file)

        rename_headers = self.raw_data.columns.values

        # We are going to manually extract the catalogNumber during search for rename,
        # every other header will just be appended automatically. Therefore, I am removing
        # the catalogNumber here so it is not duplicated
        self.rename_pieces = list(filter(lambda header: header !=
                                         "catalogNumber", rename_headers))

    @staticmethod
    def collect_files_from_folder(dir):
        # TODO: do I need to account for case here?
        accepted = ['*.csv', '*.xlsx']
        files = []
        for _type in accepted:
            files.extend(list(dict((str(f), f.stat().st_size)
                                   for f in Path(dir).glob(_type) if (f.is_file())).keys()))
        return files

    @staticmethod
    def check_valid_sources(filepath, ext):
        # check file existence
        if not os.path.exists(filepath):
            error_message("provided file does not exist in the fs")

        # check if file is actually a file
        if os.path.exists(filepath) and not os.path.isfile(filepath):
            error_message(
                "provided file is not of the correct type (i.e. it is not a file)")

    @staticmethod
    def parse_file(file_path):
        """
        Attempts to parse CSV or Excel data of specimen

        :param file_path: The os path str to the CSV file
        :type file_path: str

        :param is_csv: whether or not file is a CSV
        :type is_csv: bool

        :return: DataFrame
        """
        path_obj = Path(file_path)

        ext = path_obj.suffix

        if ext is None:
            error_message('input_file missing extension')

        ext = ext.replace('.', '')

        if ext.lower() != 'csv' and ext.lower() != 'xlsx':
            error_message(
                "input_file extension {} must match either csv or xlsx (ignoring case)".format(ext))

        Dynaiello.check_valid_sources(file_path, ext)

        raw_data = None

        if ext.lower() == 'csv':
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

        # Note: all this does is grab the last character. If there is a malformatted
        # image file, this will potentially result in invalid handling of the file
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

            viewarr = find.split('_')

            # Note: all this does is grab the last character. If there is a malformatted
            # image file, this will potentially result in invalid handling of the file
            view = viewarr[len(viewarr) - 1]

            if view not in self.views:
                print('skipping image with view not currently being targeted:', find)
                print('view found:', view)
                print('views being targeted:', self.views)
                continue

            catalogNumber = item['catalogNumber'].strip()

            new_name = self.generate_name(find, item, catalogNumber)

            if os.path.exists(os.path.join(self.destination, new_name)):
                print("skipping file:", find,
                      'as its generated name', new_name, 'already exists in destination')
            else:
                print('copying and moving file to destination:',
                      find, 'to', new_name)
                # TODO: shutil.copy goes here!

            if self.mgcl_nums[catalogNumber]:
                self.mgcl_nums[catalogNumber] = self.mgcl_nums[catalogNumber].append(
                    (find, new_name))
            else:
                self.mgcl_nums[catalogNumber] = [].append(find)

    def run(self):
        files = self.collect_files()

        # df.loc[df['column_name'] == some_value]
        for _id, item in self.raw_data.iterrows():
            filtered_list = list(filter(
                lambda fi: item['catalogNumber'].strip() in fi, files))

            if len(filtered_list) > 0:
                self.handle_items(item, filtered_list)


def cli():
    my_parser = argparse.ArgumentParser(description="Dynaiello is a version of the Aiello script with less column restrictions. Copy and rename entries based on a CSV file.",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
          Example Runs:
            python3 ./dynaiello.py --start_dir /fake/path --destination /fake/path --input_file /path/to/file.csv
            python3 ./dynaiello.py --start_dir /fake/path --destination /fake/path --input_file /path/to/file.csv --views D
            python3 ./dynaiello.py --start_dir /fake/path --destination /fake/path --input_file /path/to/file.csv --views D V L
            python3 ./dynaiello.py --start_dir /fake/path --destination /fake/path --input_group /path/to/dir/of/csv_or_xlsx_files
         '''))

    my_parser.add_argument('-s', '--start_dir', required=True,
                           type=str, help="The path to the starting directory, images will be located recursively from here")
    my_parser.add_argument('-d', '--destination', required=True,
                           type=str, help="The path to the destination directory, images will be copied to here")

    file_group = my_parser.add_mutually_exclusive_group(required=True)
    file_group.add_argument(
        '-f', '--input_file', action='store', help="The path to the CSV or XLSX of specimen data")
    file_group.add_argument(
        '-i', '--input_group', action='store', help="The path to a directory containing multiple CSV or XLSX files")

    my_parser.add_argument('-v', '--views', required=False, nargs='+', default=[
                           'V', 'D'], help="The specimen view(s) to target (i.e. D for Dorsal, V for Ventral)")

    args = my_parser.parse_args()

    start_dir = args.start_dir
    destination = args.destination
    input_file = args.input_file
    input_group = args.input_group
    views = args.views

    print("Program starting...\n")

    if (input_group is not None):
        files = Dynaiello.collect_files_from_folder(input_group)

        for f in files:
            print('Now reviewing', f)
            dynaiello = Dynaiello(start_dir, destination, f, views)
            dynaiello.run()

    else:
        dynaiello = Dynaiello(start_dir, destination, input_file, views)

    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()
