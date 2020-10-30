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

        self.init_data()

        self.files_from_start = []

    # TODO: think about what needs to be reset here
    # def reset(self):
    #     self.input_file = ''

    def init_data(self):
        self.raw_data = Dynaiello.parse_file(self.input_file)

        rename_headers = self.raw_data.columns.values

        # We are going to manually extract the catalogNumber during search for rename,
        # every other header will just be appended automatically. Therefore, I am removing
        # the catalogNumber here so it is not duplicated.
        # Note: I had to change the lambda logic to be header.find because on instances where
        # a sheet contains two catalogNumber headers, they would be assigned numbers and therefore
        # neither would get filtered out
        self.rename_pieces = list(filter(lambda header: header.find("catalogNumber") == -1
                                         and header != "end", rename_headers))

    def set_input_file(self, new_file):
        self.input_file = new_file

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

    # Note: I am not removing this, however it is CURRENTLY not in use.
    # I found that wil particularly large datasets (looking at you Catolcala)
    # it took a massive amount of time to collect.
    def collect_files(self):
        """
        Collects all image files, not marked as duplicates at and below the starting directory

        :rtype: list of str representing paths to images in fs
        """
        return list(dict((str(f), f.stat().st_size) for f in Path(self.start_dir).glob('**/*') if (f.is_file() and "duplicate" not in str(f) and Helpers.valid_image(str(f)))).keys())

    # FIXME: does not quite work, adds extension twice. I think this is an error with how I
    # obtain the view (i.e. i dont remove the extension)
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

    def handle_find(self, item, filename, file_path):
        if "downscale" in file_path:
            print("skipping duplicate image:", file_path)

        viewarr = file_path.split('_')

        # Note: all this does is grab the last character. If there is a malformatted
        # image file, this will potentially result in invalid handling of the file
        view = viewarr[len(viewarr) - 1].split(".")[0]

        if view not in self.views:
            print('skipping image with view not currently being targeted:', file_path)
            print('view found:', view)
            print('views being targeted:', self.views)
            return

        catalogNumber = item['catalogNumber'].strip()

        new_name = self.generate_name(file_path, item, catalogNumber)

        if os.path.exists(os.path.join(self.destination, new_name)):
            print("skipping file:", file_path,
                  'as its generated name', new_name, 'already exists in destination')
        else:
            print('copying and moving file to destination:',
                  file_path, 'to', new_name)
            # TODO: shutil.copy goes here!

        if self.mgcl_nums[catalogNumber]:
            self.mgcl_nums[catalogNumber] = self.mgcl_nums[catalogNumber].append(
                (file_path, new_name))
        else:
            self.mgcl_nums[catalogNumber] = [].append(file_path)

    def find_item(self, path, item):
        catalogNumber = item['catalogNumber'].strip()
        print('\nlooking for', catalogNumber, 'in', path)
        if os.path.exists(path):
            for image in sorted(os.listdir(path)):
                if catalogNumber in image:
                    self.handle_find(item, image, os.path.join(path + image))
        else:
            print(
                "warining: path is not in filesystem (skipping entry)... --> {}".format(path))

    def recursive_find_item(self, path, item):
        subdirs = Helpers.get_dirs(path)
        # print(subdirs)
        for subdir in subdirs:
            self.recursive_find_item(os.path.join(path, subdir), item)
        self.find_item(path, item)

    def run(self):
        # print('collecting files...', end=' ')
        # self.files_from_start = self.collect_files()
        # print('done...')

        # df.loc[df['column_name'] == some_value]
        for _id, item in self.raw_data.iterrows():
            # filtered_list = list(filter(
            #     lambda fi: item['catalogNumber'].strip() in fi, self.files_from_start))

            # if len(filtered_list) > 0:
            #     self.handle_items(item, filtered_list)

            self.recursive_find_item(self.start_dir, item)


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
        dynaiello = None

        for f in files:
            print('Now reviewing', f)
            if dynaiello is None:
                dynaiello = Dynaiello(start_dir, destination, f, views)
                dynaiello.run()
            else:
                dynaiello.set_input_file(f)
                dynaiello.init_data()
                dynaiello.run()

    else:
        dynaiello = Dynaiello(start_dir, destination, input_file, views)

    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()


# python3 ./dynaiello.py --start_dir /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Script_Test_Images --destination ../testing/Dynaiello --input_group /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Batch1_Catocala10-26-20
# python3 ./dynaiello.py --start_dir /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/PINNED_COLLECTION/IMAGES_UPLOADED/IMAGES_CR2_editing_complete/EREBIDAE_renamed_but_see_prob_folder/Catocala --destination ../testing/Dynaiello --input_group /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Batch1_Catocala10-26-20
