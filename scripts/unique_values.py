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
    print("unique_values.py: error:", message)
    sys.exit(1)


class Uniquer:
    def __init__(
        self, input_file, destination, group_by, group_for, encoding="ISO-8859-1"
    ):
        self.input_file = input_file
        self.encoding = encoding

        if destination is None:
            self.destination = str(Path(input_file).parent)
        else:
            self.destination = destination

        self.raw_data = Uniquer.parse_file(input_file, encoding)
        self.group_by = group_by
        self.group_for = group_for

        self.verify_grouping()

        # unique values is used when groupby statement is missing
        self.unique_values = dict()

        self.unique_frames = []

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
    def parse_file(file_path, encoding):
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

        Uniquer.check_valid_sources(file_path, ext)

        raw_data = None

        if ext.lower() == "csv":
            raw_data = pd.read_csv(file_path, encoding=encoding, low_memory=False)
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

    def verify_grouping(self):
        if self.group_by is not None:
            for col in self.group_by:
                try:
                    self.raw_data[col]
                except:
                    error_message(
                        "{} does not exist in the provided input file".format(col)
                    )

        if self.group_by is not None and self.group_for is not None:
            for col in self.group_for:
                try:
                    self.raw_data[col]
                except:
                    error_message(
                        "{} does not exist in the provided input file".format(col)
                    )

    def write_out(self):
        print("Writing values to: {}/UNIQUE_VALUES.txt".format(self.destination))
        dest_file = open(r"{}/UNIQUE_VALUES.txt".format(self.destination), "w+")

        for col in self.unique_values:
            dest_file.write("{} : [ ".format(col))
            for item in self.unique_values[col]:
                dest_file.write("{}, ".format(item))
            dest_file.write(" ]\n\n")

        dest_file.close()

    def write_groups(self):
        logfile = Uniquer.generate_logname("UNIQUE_VALUES", self.destination)
        # merged = None
        for heading, frame in self.unique_frames:
            with open(logfile, "a") as f:
                f.write(heading + "\n")
                frame.to_csv(f)
                f.write("\n")
            # this commented block merges it horizontally
            # if merged is None:
            #     merged = frame
            # else:
            #     merged = pd.concat([merged, frame], axis=1)

        # print(merged)

    def run(self):

        # print("\nParsing CSV...\n")
        # self.raw_csv_data = pd.read_csv(
        #     self.csv_path, header=0, encoding="ISO-8859-1", low_memory=False)

        if self.group_by:
            if self.group_for is not None:
                for col in self.group_for:
                    self.unique_frames.append(
                        (
                            "group_by: {},group_for: {}".format(self.group_by, col),
                            self.raw_data.groupby(self.group_by)[col].unique(),
                        )
                    )
            else:
                for col in self.raw_data:
                    if col in self.group_by:
                        continue

                    self.unique_frames.append(
                        (
                            "group_by: {},group_for: {}".format(self.group_by, col),
                            self.raw_data.groupby(self.group_by)[col].unique(),
                        )
                    )

            self.write_groups()

        else:
            for col in self.raw_data:
                self.unique_values[col] = self.raw_data[col].unique()
            self.write_out()


def cli():
    my_parser = argparse.ArgumentParser(
        description="unique_values is an upgraded version of the UniqueCols utility used to find all the unique values in each column of a CSV or XLSX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
          Example Runs:
            python3 ./unique_values.py --input_file /path/to/file.csv
            python3 ./unique_values.py --input_file /path/to/file.csv --group_by columnName
            python3 ./unique_values.py --destination /fake/path --input_file /path/to/file.csv  --group_by columnName secondColumnName
         """
        ),
    )

    my_parser.add_argument(
        "-d",
        "--destination",
        required=False,
        type=str,
        help="The path to the destination directory, the output will be written here (default is input_file directory)",
    )
    my_parser.add_argument(
        "-f", "--input_file", action="store", help="The path to the CSV or XLSX"
    )

    my_group = my_parser.add_argument_group()
    my_group.add_argument(
        "-g",
        "--group_by",
        action="store",
        nargs="+",
        required=False,
        help="The grouping logic for finding unique values (this works similarly to a SQL group by)",
    )
    my_group.add_argument(
        "-t",
        "--group_for",
        action="store",
        nargs="+",
        required=False,
        help="The column(s) that the grouping is in terms of (cannot be columns in the group_by). Defaults to all",
    )
    my_parser.add_argument(
        "-e",
        "--encoding",
        required=False,
        default="ISO-8859-1",
        help="Override the encoding interpretation of the passed in file (default is ISO-8859-1, utf8 is another option)",
    )

    args = my_parser.parse_args()

    destination = args.destination
    input_file = args.input_file
    group_by = args.group_by
    group_for = args.group_for
    encoding = args.encoding

    print("Program starting...\n")

    uniquer = Uniquer(input_file, destination, group_by, group_for, encoding)
    uniquer.run()

    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()
