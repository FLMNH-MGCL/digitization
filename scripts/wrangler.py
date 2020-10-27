import gspread  # https://gspread.readthedocs.io/en/latest/index.html
import os
import sys
import argparse
import textwrap
import re
import pandas as pd
from pathlib import Path, PureWindowsPath
from Helpers import Helpers


def error_message(message):
    print("wrangler.py: error:", message)
    sys.exit(1)


class FSLocation:
    def __init__(self, dorsal, ventral, parent_directory, path):
        self.dorsal = dorsal
        self.ventral = ventral
        self.parent_directory = parent_directory
        self.path = path


class Specimen:
    def __init__(self, catalog_number, other_catalog_numbers, family, sci_name, genus, spec_epithet, record_id, references):
        self.bombID = None
        self.catalog_number = catalog_number
        self.other_catalog_numbers = other_catalog_numbers
        self.family = family
        self.sci_name = sci_name
        self.genus = genus
        self.spec_epithet = spec_epithet
        self.record_id = record_id
        self.references = references

        self.location = None

    def __str__(self):
        return "\tbombID: {},\n\tcatalogNumber: {},\n\totherCatalogNumber: {},\n\tfamily: {},\n\tgenus: {},\n\tsepcies: {},\n\trecordId: {},\n\trefs: {},\n\tlocation_obj: {}".format(self.bombID, self.catalog_number, self.other_catalog_numbers, self.family, self.genus, self.spec_epithet, self.record_id, self.references, self.location)


class GDriveConnector:
    def __init__(self, sheet_id, config_location):
        self.sheet_id = sheet_id
        self.config = config_location

        try:
            print("connecting to Google Sheet document... ", end="")
            self.connection = gspread.service_account(filename=config_location)
            self.document = self.connection.open_by_key(self.sheet_id)
            print("success!")
            print("currently viewing document:", self.document.title)
        except Exception as error:
            print("failed!")
            error_message(error)

    @staticmethod
    def extract_id(url):
        return re.search(r"/d/(.*)/", url)


class Wrangler:
    def __init__(self, start_dir, config_location, excel_file, csv_file, sheet_id, sheet_url):
        if sheet_url is not None:
            # get ID
            _id = GDriveConnector.extract_id(sheet_url)

            # attempt to get ID from regex match obj
            if _id is None:
                error_message(
                    "could not extract ID from URL to make GDrive Connection")
            else:
                try:
                    print(_id.group(1), config_location)
                    self.gconnection = GDriveConnector(
                        str(_id.group(1)), config_location)
                except:
                    error_message(
                        "could not extract ID from URL to make GDrive Connection")

        else:
            self.gconnection = GDriveConnector(sheet_id, config_location)

        if excel_file is None:
            self.csv_file = csv_file
            self.raw_data = Wrangler.parse_file(self.csv_file, True)
        else:
            self.excel_file = excel_file
            self.raw_data = Wrangler.parse_file(self.excel_file, False)

        self.start_dir = start_dir

        # { catalog_number : specimen_obj }
        self.specimens = dict()

        # {catalog_number : [objects] }
        self.duplicates = dict()

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

        Wrangler.check_valid_sources(file_path, ext)

        raw_data = None

        if is_csv:
            raw_data = pd.read_csv(file_path)
        else:
            raw_data = pd.read_excel(file_path)

        return raw_data

    def add_duplicate(self, specimen):
        if specimen.catalog_number in self.duplicates:
            self.duplicates[specimen.catalog_number] = self.duplicates[specimen.catalog_number].append(
                specimen)
        else:
            existing_specimen = self.specimens[specimen.catalog_number]
            self.duplicates[specimen.catalog_number] = [
                existing_specimen, specimen]

    @staticmethod
    def extract_catalog_number(filepath):
        file_obj = Path(filepath)
        filename = file_obj.stem

        pattern = r'MGCL_[0-9]+'
        catalog_number_matches = re.search(pattern, filename, re.IGNORECASE)

        if not catalog_number_matches:
            return None

        catalog_number = catalog_number_matches.group()

        if catalog_number == "":
            return None

        return catalog_number

    @staticmethod
    def extract_family_genus(filepath):
        pattern = r"[a-z]*dae[\\/][a-z]*"
        family_genus = re.search(pattern, filepath, re.IGNORECASE)

        if not family_genus:
            return None

        family_genus = family_genus.group()

        if family_genus == "":
            return None

        try:
            family_genus = PureWindowsPath(family_genus).as_posix()
        except:
            # not on windows, no need to worry about this
            family_genus = family_genus.group()
            pass

        family_genus_vec = family_genus.split("/")

        if len(family_genus_vec) < 2:
            return None

        return family_genus_vec

    def collect_files(self):
        """ 
        Collects all image files, not marked as duplicates at and below the starting directory

        :rtype: list of str representing paths to images in fs
        """
        return list(dict((str(f), f.stat().st_size) for f in Path(self.start_dir).glob('**/*') if (f.is_file() and "duplicate" not in str(f) and Helpers.valid_image(str(f)))).keys())

    def init_dict(self):
        print("Analyzing local file passed in...\n")

        for i, (_, row) in enumerate(self.raw_data.iterrows()):
            if i == 0:
                continue

            try:
                catalog_number = str(row['catalogNumber'])
                other_catalog_numbers = str(row['otherCatalogNumbers'])
                family = str(row['family'])
                sci_name = str(row['scientificName'])
                genus = str(row['genus'])
                spec_epithet = str(row['specificEpithet'])
                record_id = str(row['recordId'])
                references = str(row['references'])

                specimen = Specimen(catalog_number, other_catalog_numbers,
                                    family, sci_name, genus, spec_epithet, record_id, references)

                if catalog_number in self.specimens:
                    print("Duplicate found: {} @ row {}".format(catalog_number, i))
                    self.add_duplicate(specimen)
                else:
                    self.specimens[catalog_number] = specimen

            except:
                e = sys.exc_info()[0]
                error_message(
                    "Something went wrong when parsing this row: {}\n\nExact error: \n{}\n".format(i + 1, e))

        print("\nAll rows handled, specimen objects created")

    def find_in_fs(self):
        print("Searching fs for files, this may take some time...\n")
        # collect all files
        files = self.collect_files()

        # for each file in list
        for f in files:
            catalog_number = Wrangler.extract_catalog_number(f)
            family_genus = Wrangler.extract_family_genus(f)

            if catalog_number is None:
                pass

            if family_genus is None:
                pass

            family = family_genus[0]
            genus = family_genus[1]

            if catalog_number in self.specimens:
                # check if family and genus match
                specimen = self.specimens[catalog_number]

                if specimen.family == family and specimen.genus == genus:
                    # do something here
                    # TODO: add check for species too? not sure if this is something
                    # extractable from the path

                    # should add the location data if this check passes
                    pass
                else:
                    # log this, found MGCL number but information differs about its
                    # data than what was extracted from CSV
                    pass

    def connect_with_drive(self):
        pass

    def run(self):
        # create the specimen objects
        self.init_dict()
        self.find_in_fs()
        self.connect_with_drive()

        print("\nPrinting duplicate entries...\n")
        for key, arr in self.duplicates.items():
            print(key)
            for spec in arr:
                print(spec, end="\n\n")
            print()


# TESTING GC FUNCTIONS, KEEPING FOR NOW FOR REFERENCE

# config.json is the bot's configuration data, including its credentials/api keys and what not
# therefore, it is not included in the repo
# gc = gspread.service_account(filename='config.json')

# this key does not matter, which is why I didn't remove it before pushing.
# sh = gc.open_by_key('1IIAp5sDSq61x1ZRmtbtcOSXoJ0QglJtilI6M6gUY3Dw')

# worksheets = sh.worksheets()

# seq_id_worksheet = worksheets[0]

# seq_id_headers = seq_id_worksheet.row_values(1)

# print(seq_id_headers)

def cli():
    my_parser = argparse.ArgumentParser(description="Populate a remote Google Sheet with specimen that match a set of requirements given a CSV",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
          Example Runs:
            python3 ./wrangler.py --start_dir /fake/path --csv_file /path/to/file.csv --config ./config.json --sheet_id 1IIAp5sDSq61x1ZRmtbtcOSXoJ0QglJtilI6M6gUY3Dw\n
            python3 ./wrangler.py --start_dir /fake/path --csv_file /path/to/file.csv --config ./config.json --sheet_url https://docs.google.com/spreadsheets/d/1IIAp5sDSq61x1ZRmtbtcOSXoJ0QglJtilI6M6gUY3Dw/edit#gid=1483107405
         '''))

    my_parser.add_argument('-d', '--start_dir', required=True,
                           type=str, help="path to the starting directory")
    my_parser.add_argument('-c', '--config', action='store',
                           required=True, help="path to the config.json")

    group_files = my_parser.add_mutually_exclusive_group(required=True)
    group_files.add_argument(
        '-f', '--csv_file', action='store', help="path to CSV of specimen data")
    group_files.add_argument(
        '-e', '--excel_file', action='store', help="path to XLSX of specimen data")

    group = my_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--sheet_id', action='store',
                       help='the ID extracted from the URL of the Google Sheet document')
    group.add_argument('-u', '--sheet_url', action='store',
                       help="the full URL of the Google Sheet document")

    args = my_parser.parse_args()

    start_dir = args.start_dir
    csv_file = args.csv_file
    excel_file = args.excel_file
    config = args.config
    sheet_id = args.sheet_id
    sheet_url = args.sheet_url

    wrangler = Wrangler(start_dir, config, excel_file,
                        csv_file, sheet_id, sheet_url)

    print("Program starting...\n")
    wrangler.run()
    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()


"""
fake tests:
python3 wrangler.py -d /fake/path -c ./config.json -f /fake/file.csv -i fakeid 
python3 wrangler.py -d /fake/path -c ./config.json -f /fake/file.csv -i fakeid -u fakeurl.com
python3 wrangler.py -d /fake/path -c ./config.json -f /fake/file.csv -e /fake/excel.xlsx -i fakeid
"""


"""
wrangler overview:

CREATE DICTIONARY
==================
given excel sheet:
  make dictionary -> map MGCL nums to specimen info
  loop rows:
    location obj: { dorsal, ventral, parent_directory }
    specimen obj: { bombID, catalogNumber, otherCatalogNumber, family, genus, sepcies, recordId, refs, location_obj }
    { catalogNumber : specimen_obj }

CHECK IMG EXISTENCE IN FS
=========================
given provided start in filesystem:
  grab all files
  loop files:
    destructure path to obtain family, genus, species
    destructure filename to object mgcl
    attempt access of dictionary by mgcl
      if success -> update object with location data

OBTAIN UI
============
load premade dictionary of UIs
loop dictionary entries:
  attempt access of UI by family, genus, species
    if get UI -> assign object bombID

then what?
"""
