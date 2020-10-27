from enum import Enum, unique
import sys
import os
import pandas as pd
import pathlib
import shutil
import argparse
import textwrap
from datetime import datetime


def error_message(message, exit=True):
    print("relocate.py: error:", message)

    if exit:
        sys.exit(1)


@unique
class ConfigTypes(Enum):
    DEFAULT = "DEFAULT"
    MGCLCHECKER = "MGCLCHECKER"

    def __eq__(self, rhs):
        return self.name == rhs


class Relocator:
    """
    Rather than document each individual class method, I will overview this class here.
    Relocator will execute multiple shutil.copyfile commands based on the log file 
    generated from another script. Some scripts that filter out troublesome / bad
    data output logs containing the paths to said data. Each script may have a slightly 
    different logging format, which is why each script has its own corresponding class method 
    (e.g. the MGCLChecker script has its own self.mgclchecker method). The general outline for 
    each function is as follows:

    iterate through each row of the log csv file
    grab the path of bad data point
    copy data to new location
    """

    def __init__(self, config=ConfigTypes.DEFAULT, log_location="", destination=""):
        self.config = config
        self.log_location = log_location
        self.destination = destination
        self.failures = []

    @staticmethod
    def check_valid_construction(log, destination):
        """
        Checks validity of log file and destination directory. Will sys.exit on invalid 
        file or directory
        """
        if not os.path.exists(log) and not os.path.isfile(log) and pathlib.Path(log).suffix != ".csv":
            error_message(
                "{} either does not exist or is the wrong file type".format(log))

        if not os.path.exists(destination) and not os.path.isdir(destination):
            error_message(
                "{} either does not exist or is not a directory".format(destination))

    def relocate(self, old_location, filename):
        new_filename = filename
        tentative_path = os.path.abspath(
            os.path.join(self.destination, new_filename))
        raw_path = pathlib.Path(tentative_path)
        ext = raw_path.suffix
        i = 1

        while os.path.exists(tentative_path):
            new_filename = raw_path.stem + "_DUP_{}".format(i)
            tentative_path = os.path.abspath(os.path.join(
                self.destination, "{}{}".format(new_filename, ext)))
            i += 1

        print("attempting copy of {} to {}".format(
            old_location, tentative_path))
        shutil.copyfile(old_location, tentative_path)

    def mgclchecker(self):
        raw_data = pd.read_csv(self.log_location)

        for _, row in raw_data.iterrows():
            path = ""

            try:
                path = str(row['path'])
            except:
                error_message(
                    "csv file improperly formatted for MGCLChecker relocation. attempted access to 'path' header, returned None")

            filename = os.path.basename(path)
            try:
                old_location = os.path.abspath(path)
                self.relocate(old_location, filename)

                # shutil.copyfile(old_location, new_location)
            except Exception as exception:
                error_message("{}... failed to copy {}... skipping".format(
                    exception, old_location), False)
                self.failures.append(old_location)

            print()

    def run(self):
        """
        Runs the appropriate method according to the config selected. E.g. If config
        if MGCLCHECKER then self.mgclchecker will be executed.
        """
        if self.config == ConfigTypes.MGCLCHECKER:
            self.mgclchecker()


# TODO: make me so I can import this file into other python scripts
def lib():
    pass


def cli():
    """
    Runs the CLI version of this script: collects arguments and intitializes the Relocator class accordingly
    """
    my_parser = argparse.ArgumentParser(description="Relocate troublesome images based on the log output of other scripts",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
          Config Types:
            MGCLCHECKER

          Example Runs:
            python3 ./relocate.py --config MGCLCHECKER --log /path/to/log.csv --destination /new/parent/directory
         '''))

    my_parser.add_argument('-c', '--config', required=True, type=str,
                           help="the log type (based on script that generated it)")
    my_parser.add_argument('-l', '--log', required=True,
                           type=str, help="path to the log file")
    my_parser.add_argument('-d', '--destination', required=True,
                           type=str, help="path to the new directory")

    args = my_parser.parse_args()

    try:
        config = ConfigTypes[args.config]
    except:
        error_message(
            "{} is not a valid config type. run '--help' to see all accepted configurations")

    log = args.log
    destination = args.destination

    Relocator.check_valid_construction(log, destination)

    relocator = Relocator(config, os.path.abspath(log),
                          os.path.abspath(destination))
    print("Program starting...\n")
    relocator.run()
    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()
