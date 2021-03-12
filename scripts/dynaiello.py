import os
import sys
import argparse
import textwrap
import re
import pandas as pd
import datetime
import shutil
from pathlib import Path, PureWindowsPath
from Helpers import Helpers


def error_message(message):
    print("dynaiello.py: error:", message)
    sys.exit(1)


class DataPoint:
    def __init__(self, catalogNumber, found_at="", relocated_to=""):
        self.catalogNumber = catalogNumber
        self.found_at = found_at
        self.relocated_to = relocated_to


# its like Aiello, but a little more dynamic (hence, dynaiello)
class Dynaiello:
    def __init__(self, start_dir, destination, input_file, views):
        self.start_dir = start_dir
        self.destination = destination
        self.views = views
        self.input_file = input_file
        self.mgcl_nums = dict()

        # { input file : { mgcl_num : [list of occurrences] } }
        self.runs = dict()

        self.init_data()

        self.files_from_start = []

    def clear_mgcl_nums(self):
        self.mgcl_nums.clear()

    def init_data(self):
        self.raw_data = Dynaiello.parse_file(self.input_file)

        rename_headers = self.raw_data.columns.values

        # We are going to manually extract the catalogNumber during search for rename,
        # every other header will just be appended automatically. Therefore, I am removing
        # the catalogNumber here so it is not duplicated.
        # Note: I had to change the lambda logic to be header.find because on instances where
        # a sheet contains two catalogNumber headers, they would be assigned numbers and therefore
        # neither would get filtered out
        self.rename_pieces = list(
            filter(
                lambda header: header.find("catalogNumber") == -1
                and header.lower() != "end"
                and header.lower() != "start"
                and header.lower() != "synonym",
                rename_headers,
            )
        )

    def set_input_file(self, new_file):
        self.input_file = new_file

    @staticmethod
    def collect_files_from_folder(dir):
        # TODO: do I need to account for case here?
        accepted = ["*.csv", "*.xlsx"]
        files = []
        for _type in accepted:
            files.extend(
                list(
                    dict(
                        (str(f), f.stat().st_size)
                        for f in Path(dir).glob(_type)
                        if (f.is_file())
                    ).keys()
                )
            )
        return files

    @staticmethod
    def check_valid_sources(filepath, ext):
        # check file existence
        if not os.path.exists(filepath):
            error_message("provided file does not exist in the fs")

        # check if file is actually a file
        if os.path.exists(filepath) and not os.path.isfile(filepath):
            error_message(
                "provided file is not of the correct type (i.e. it is not a file)"
            )

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
            error_message("input_file missing extension")

        ext = ext.replace(".", "")

        if ext.lower() != "csv" and ext.lower() != "xlsx":
            error_message(
                "input_file extension {} must match either csv or xlsx (ignoring case)".format(
                    ext
                )
            )

        Dynaiello.check_valid_sources(file_path, ext)

        raw_data = None

        if ext.lower() == "csv":
            raw_data = pd.read_csv(file_path)
        else:
            raw_data = pd.read_excel(file_path)

        return raw_data

    @staticmethod
    def generate_logname(log_id, filepath):
        d = datetime.datetime.today()
        date = "{}_{}_{}".format(str(d.year), str(d.month), str(d.day))

        ext = ".csv"

        filename = "{}_{}{}".format(os.path.join(filepath, log_id), date, ext)

        return filename

    # Note: I am not removing this, however it is CURRENTLY not in use.
    # I found that wil particularly large datasets (looking at you Catolcala)
    # it took a massive amount of time to collect.
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

    # FIXME: does not quite work, adds extension twice. I think this is an error with how I
    # obtain the view (i.e. i dont remove the extension)
    def generate_name(self, found, item, catalogNumber):
        ext = found.split(".")[1]
        viewarr = found.split("_")

        # Note: all this does is grab the last character. If there is a malformatted
        # image file, this will potentially result in invalid handling of the file
        view = viewarr[len(viewarr) - 1]

        view = re.sub(r"\..*", "", view)

        new_name = ""

        for piece in self.rename_pieces:
            if item[piece] is not None and not pd.isnull(item[piece]):
                print(piece, item[piece])
                new_name += "{}_".format(str(item[piece]))

        if "view" in self.rename_pieces:
            new_name += "{}.{}".format(catalogNumber, ext)
        else:
            # NOTE: notice the formatting is now different when the user does not
            # specify the view in the CSV file. The format will therefore default to
            # MGCL_#####_VIEW.EXT. if this should be reverse, just swap the variable
            # order passed to .format
            new_name += "{}_{}.{}".format(catalogNumber, view, ext)

        return new_name

    def append_data_point(self, data_point):
        catalogNumber = data_point.catalogNumber
        if catalogNumber in self.mgcl_nums:
            self.mgcl_nums[catalogNumber].append(data_point)
        else:
            new_list = []
            new_list.append(data_point)
            self.mgcl_nums[catalogNumber] = new_list

    def handle_find(self, item, filename, file_path):
        print("\nFound an instance!...")

        # I want this to throw an error, so it is outside try block
        catalogNumber = item["catalogNumber"].strip()

        if "downscale" in file_path:
            print("skipping duplicate image:", file_path)

            data_point = DataPoint(catalogNumber, file_path)
            self.append_data_point(data_point)
            return

        viewarr = file_path.split("_")

        # Note: all this does is grab the last character. If there is a malformatted
        # image file, this will potentially result in invalid handling of the file
        view = viewarr[len(viewarr) - 1]
        view = re.sub(r"\..*", "", view)

        csvView = None

        try:
            # TODO: should this be a list??
            csvView = item["view"].strip()
        except Exception:
            # I don't really need to do anything
            pass

        if csvView is None:
            if view not in self.views:
                print(
                    "skipping image with view not currently being targeted:", file_path
                )
                print("view found:", view)
                print("views being targeted:", self.views)

                data_point = DataPoint(catalogNumber, file_path)
                self.append_data_point(data_point)

                return

        else:
            # TODO: should this lowercase compare or fail if not case match?
            if view.lower() != csvView.lower():
                print(
                    "skipping image with view not currently being targeted:", file_path
                )
                print("view found:", view)
                print("views being targeted:", csvView)

                data_point = DataPoint(catalogNumber, file_path)
                self.append_data_point(data_point)

                return

        new_name = self.generate_name(file_path, item, catalogNumber)

        if os.path.exists(os.path.join(self.destination, new_name)):
            print(
                "skipping file:",
                file_path,
                "as its generated name",
                new_name,
                "already exists in destination",
            )

            data_point = DataPoint(catalogNumber, file_path)
            self.append_data_point(data_point)

        else:
            print(
                "copying and moving file to destination:",
                file_path,
                "to",
                os.path.join(self.destination, new_name),
                "\n",
            )

            shutil.copy(file_path, os.path.join(self.destination, new_name))

            data_point = DataPoint(
                catalogNumber, file_path, os.path.join(
                    self.destination, new_name)
            )

            self.append_data_point(data_point)

    def find_item(self, path, item):
        catalogNumber = item["catalogNumber"].strip()
        print("looking in {}...".format(path))
        if os.path.exists(path):
            for image in sorted(os.listdir(path)):
                if catalogNumber in image:
                    self.handle_find(item, image, os.path.join(path, image))
        else:
            print(
                "warining: path is not in filesystem (skipping entry)... --> {}".format(
                    path
                )
            )

    # maybe add check for unix platform, and use find here instead?

    def recursive_find_item(self, path, item):
        subdirs = Helpers.get_dirs(path)

        for subdir in subdirs:
            self.recursive_find_item(os.path.join(path, subdir), item)

        self.find_item(path, item)

    def write_log(self):
        log_filename = Dynaiello.generate_logname(
            "DYNAIELLO", self.destination)

        with open(log_filename, "a") as log:
            log.write("sheet_name,catalogNumber,found_at,relocated_to\n")
            for filename in self.runs:
                for mgcl_num in self.runs[filename]:
                    data_set = self.runs[filename][mgcl_num]
                    for data_point in data_set:
                        print(
                            "{},{},{},{}\n".format(
                                filename,
                                data_point.catalogNumber,
                                data_point.found_at,
                                data_point.relocated_to,
                            )
                        )
                        log.write(
                            "{},{},{},{}\n".format(
                                filename,
                                data_point.catalogNumber,
                                data_point.found_at,
                                data_point.relocated_to,
                            )
                        )

    def run(self):

        for _id, item in self.raw_data.iterrows():
            try:
                print("\nLooking for {}...\n".format(item["catalogNumber"]))
            except Exception:
                print(
                    "dynaiello.py: error: no catalogNumber column present... skipping entry"
                )
                continue

            # TODO: add wrapping try block?
            self.recursive_find_item(self.start_dir, item)

            # was never found
            if item["catalogNumber"] not in self.mgcl_nums:
                data_point = DataPoint(item["catalogNumber"])
                self.append_data_point(data_point)

        self.runs[self.input_file] = self.mgcl_nums


def cli():
    my_parser = argparse.ArgumentParser(
        description="Dynaiello is a version of the Aiello script with less column restrictions. Copy and rename entries based on a CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
          Example Runs:
            python3 ./dynaiello.py --start_dir /fake/path --destination /fake/path --input_file /path/to/file.csv
            python3 ./dynaiello.py --start_dir /fake/path --destination /fake/path --input_file /path/to/file.csv --views D
            python3 ./dynaiello.py --start_dir /fake/path --destination /fake/path --input_file /path/to/file.csv --views D V L
            python3 ./dynaiello.py --start_dir /fake/path --destination /fake/path --input_group /path/to/dir/of/csv_or_xlsx_files
         """
        ),
    )

    my_parser.add_argument(
        "-s",
        "--start_dir",
        required=True,
        type=str,
        help="The path to the starting directory, images will be located recursively from here",
    )
    my_parser.add_argument(
        "-d",
        "--destination",
        required=True,
        type=str,
        help="The path to the destination directory, images will be copied to here",
    )

    file_group = my_parser.add_mutually_exclusive_group(required=True)
    file_group.add_argument(
        "-f",
        "--input_file",
        action="store",
        help="The path to the CSV or XLSX of specimen data",
    )
    file_group.add_argument(
        "-i",
        "--input_group",
        action="store",
        help="The path to a directory containing multiple CSV or XLSX files",
    )

    my_parser.add_argument(
        "-v",
        "--views",
        required=False,
        nargs="+",
        default=["V", "D"],
        help="The specimen view(s) to target (i.e. D for Dorsal, V for Ventral)",
    )

    args = my_parser.parse_args()

    start_dir = args.start_dir
    destination = args.destination
    input_file = args.input_file
    input_group = args.input_group
    views = args.views

    print("Program starting...\n")

    if input_group is not None:
        files = Dynaiello.collect_files_from_folder(input_group)
        dynaiello = None

        if len(files) == 0:
            print("No valid files could be pulled from: {}...".format(input_group))
            print(
                "\nPlease ensure there are CSV or XLSX files at the root of the folder"
            )

        for f in files:
            print("Now reviewing", f)
            if dynaiello is None:
                # start condition
                dynaiello = Dynaiello(start_dir, destination, f, views)
                dynaiello.run()
            else:
                # clear past run contents
                dynaiello.set_input_file(f)
                dynaiello.init_data()
                dynaiello.clear_mgcl_nums()
                dynaiello.run()

    else:
        dynaiello = Dynaiello(start_dir, destination, input_file, views)

    dynaiello.write_log()

    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()


# python3 ./dynaiello.py --start_dir /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Script_Test_Images --destination /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Script_Test_Destination --input_group /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Batch1_Catocala10-26-20/Pulled
# python3 ./dynaiello.py --start_dir /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Script_Test_Images --destination ../testing/Dynaiello/output --input_group ../testing/Dynaiello/input


# meh tests
# python3 ./dynaiello.py --start_dir /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/PINNED_COLLECTION/IMAGES_UPLOADED/IMAGES_CR2_editing_complete/EREBIDAE_renamed_but_see_prob_folder/Catocala --destination ../testing/Dynaiello --input_group /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Batch1_Catocala10-26-20
# python3 ./dynaiello.py --start_dir /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Script_Test_Images --destination ../testing/Dynaiello --input_group /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/SPECIAL_PROJECTS/Catocala_Nick_Homziak/Batch1_Catocala10-26-20/Needs_full_rename
