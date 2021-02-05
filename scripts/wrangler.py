import gspread  # https://gspread.readthedocs.io/en/latest/index.html
import os
import sys
import argparse
import textwrap
import re
import pandas as pd
from pathlib import Path, PureWindowsPath
import glob
from Helpers import Helpers
import logging
import inspect


def error_message(message):
    print("wrangler.py: error:", message)
    sys.exit(1)


def str_cmp(str1, str2, ignore_case=True):
    if ignore_case:
        return str1.lower() == str2.lower()
    else:
        return str1 == str2


def reset_row(row):
    row["Image1_file_name"] = None
    row["Image2_file_name"] = None
    row["catalogNumber"] = None
    row["otherCatalogNumbers"] = None
    row["Author"] = None
    row["Year"] = None
    row["Original comb?"] = None
    row["Last edited date"] = None
    row["Nomenclatural notes"] = None
    row["recordId"] = None
    row["references"] = None
    row["scan_id"] = None

    return row


class FSLocation:
    def __init__(self, dorsal, ventral, parent_directory, path):
        self.dorsal = dorsal
        self.ventral = ventral
        self.parent_directory = parent_directory
        self.path = path


class Specimen:
    def __init__(
        self,
        catalog_number,
        other_catalog_numbers,
        family,
        sci_name,
        genus,
        spec_epithet,
        record_id,
        references,
    ):
        self.bombID = None
        self.catalog_number = catalog_number
        self.other_catalog_numbers = other_catalog_numbers
        self.family = family
        self.sci_name = sci_name
        self.genus = genus
        self.spec_epithet = spec_epithet
        self.record_id = record_id
        self.references = references

        self.occurrences = []

    def __str__(self):
        return "\tbombID: {},\n\tcatalogNumber: {},\n\totherCatalogNumber: {},\n\tfamily: {},\n\tgenus: {},\n\tsepcies: {},\n\trecordId: {},\n\trefs: {},\n\toccurrences: {}".format(
            self.bombID,
            self.catalog_number,
            self.other_catalog_numbers,
            self.family,
            self.genus,
            self.spec_epithet,
            self.record_id,
            self.references,
            self.occurrences,
        )


class GDriveConnector:
    def __init__(self, sheet_id, sheet_url, config_location):
        self.sheet_id = sheet_id
        self.sheet_url = sheet_url
        self.config = config_location

        if sheet_url:
            try:
                print("attempting drive connection by url...", end="")
                self.connection = gspread.service_account(filename=config_location)
                self.document = self.connection.open_by_url(self.sheet_url)
                print("success!")

            except Exception as error:
                print("failed!\n")
                error_message(error)
        else:
            try:
                print("attempting drive connection by key... ", end="")
                self.connection = gspread.service_account(filename=config_location)
                self.document = self.connection.open_by_key(self.sheet_id)
                print("success!")
                print(self.document.worksheet("MGCL_Image_IDs"))

            except Exception as error:
                print("failed!")
                error_message(error)

    @staticmethod
    def extract_id(url):
        return re.search(r"/d/(.*)/", url)


class Wrangler:
    def __init__(
        self,
        start_dir,
        config_location,
        excel_file,
        csv_file,
        sheet_id,
        sheet_url,
        worksheet,
        narrow,
    ):
        if sheet_url is not None:
            self.gconnection = GDriveConnector(None, sheet_url, config_location)

        else:
            self.gconnection = GDriveConnector(sheet_id, None, config_location)

        if excel_file is None:
            self.csv_file = csv_file
            self.raw_data = Wrangler.parse_file(self.csv_file, True)
        else:
            self.excel_file = excel_file
            self.raw_data = Wrangler.parse_file(self.excel_file, False)

        self.start_dir = start_dir

        logging.basicConfig(
            level=logging.NOTSET,
            filename=os.path.join(start_dir, "wrangler.log"),
            filemode="w",
            format="%(levelname)s - %(message)s\n",
        )

        self.worksheet = worksheet

        # { catalog_number : specimen_obj }
        self.specimens = dict()

        # {catalog_number : [objects] }
        self.duplicates = dict()

        self.narrow = narrow

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

        # check file extension
        # TODO: update to use pathlib
        file_vec = os.path.basename(filepath).split(".")
        if len(file_vec) < 2:
            error_message("provided file is missing a valid extension")

        passed_ext = file_vec[1]

        if ext != passed_ext.lower():
            error_message(
                "passed extension {} must match either csv or xlsx".format(passed_ext)
            )

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
            self.duplicates[specimen.catalog_number] = self.duplicates[
                specimen.catalog_number
            ].append(specimen)
        else:
            existing_specimen = self.specimens[specimen.catalog_number]
            self.duplicates[specimen.catalog_number] = [existing_specimen, specimen]

    @staticmethod
    def extract_catalog_number(filepath):
        file_obj = Path(filepath)
        filename = file_obj.stem

        pattern = r"MGCL_[0-9]+"
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

        if self.narrow:
            globs = []
            for family in self.narrow:
                startPath = os.path.join(self.start_dir, family)

                print("searching for", family, "at", startPath, end="...")

                globs += glob.glob(
                    "{}/**/*.*".format(os.path.join(self.start_dir, family))
                )

            return globs

        else:
            return glob.glob("{}/**/*.*".format(self.start_dir))

    def init_dict(self):
        print("Analyzing local file passed in...")

        for i, (_, row) in enumerate(self.raw_data.iterrows()):
            if i == 0:
                continue

            try:
                catalog_number = str(row["catalogNumber"])
                other_catalog_numbers = str(row["otherCatalogNumbers"])
                family = str(row["family"])
                sci_name = str(row["scientificName"])
                genus = str(row["genus"])
                spec_epithet = str(row["specificEpithet"])
                record_id = str(row["recordId"])
                references = str(row["references"])

                specimen = Specimen(
                    catalog_number,
                    other_catalog_numbers,
                    family,
                    sci_name,
                    genus,
                    spec_epithet,
                    record_id,
                    references,
                )

                if catalog_number in self.specimens:
                    print("Duplicate found: {} @ row {}".format(catalog_number, i))
                    self.add_duplicate(specimen)
                else:
                    self.specimens[catalog_number] = specimen

            except:
                e = sys.exc_info()[0]
                error_message(
                    "Something went wrong when parsing this row: {}\n\nExact error: \n{}\n".format(
                        i + 1, e
                    )
                )

        print("All rows handled, specimen objects created\n")

    def find_in_fs(self):
        print("Searching fs for files, this may take some time...\n")
        # collect all files
        files = self.collect_files()

        # for each file in list
        for f in files:
            if not Helpers.valid_image(f) or "duplicate" in f:
                continue

            catalog_number = Wrangler.extract_catalog_number(f)
            family_genus = Wrangler.extract_family_genus(f)

            if catalog_number is None:
                logging.warning("Could not extract catalogNumber from {}".format(f))
                continue

            if family_genus is None:
                logging.warning(
                    "Could not extract family/genus information from {}".format(f)
                )
                continue

            family = family_genus[0]
            genus = family_genus[1]

            if catalog_number in self.specimens:
                # check if family and genus match
                specimen = self.specimens[catalog_number]

                if not isinstance(specimen, Specimen):
                    logging.warning(
                        "Invalid specimen detected from csv/excel: {}".format(specimen)
                    )
                    continue

                if str_cmp(specimen.family, family) and str_cmp(specimen.genus, genus):
                    # it doesn't match when factoring in case
                    if str_cmp(specimen.family, family, False) or str_cmp(
                        specimen.genus, genus, False
                    ):
                        logging.warning(
                            "Detected mixed capitalization @ {}\nExpected Family,Genus: {},{}\nFound:{},{}".format(
                                catalog_number,
                                family,
                                genus,
                                specimen.family,
                                specimen.genus,
                            )
                        )

                    # append to specimen occurrences
                    specimen.occurrences.append(f)
                    logging.info(
                        "Appended {} to list of occurrences @ {}...".format(
                            catalog_number, f
                        )
                    )
                else:
                    # log this, found MGCL number but information differs about its
                    # data than what was extracted from CSV
                    logging.warning(
                        "Found {} @ {} - information differs about its data than what was extracted from csv/xlsx...\nExpected Family,Genus: {},{}\nFound: {},{}".format(
                            catalog_number,
                            f,
                            family,
                            genus,
                            specimen.family,
                            specimen.genus,
                        )
                    )

    def iter_specimen(self, df):

        df_dict = df.to_dict("records")

        for catalogNumber, specimen in self.specimens.items():
            if not isinstance(specimen, Specimen):
                logging.warning(
                    "Invalid specimen detected from csv/excel: {}".format(specimen)
                )
                continue

            if not specimen.family or not specimen.genus or not specimen.spec_epithet:
                logging.warning(
                    "Family, Genus and Specific Epithet missing from specimen: "
                    + str(specimen)
                )

                continue

            matches = list(
                filter(
                    lambda item: item["Family"] == specimen.family
                    and item["Genus"] == specimen.genus
                    and item["Species"] == specimen.spec_epithet,
                    df_dict,
                )
            )

            needs_new_row = True

            for row in matches:
                if (
                    row["catalogNumber"]
                    or row["Image1_file_name"]
                    or row["Image2_file_name"]
                ):
                    continue

                else:
                    row["catalogNumber"] = catalogNumber

                    if len(specimen.occurrences) > 0:
                        row["Image1_file_name"] = Path(specimen.occurrences[0]).stem

                        if len(specimen.occurrences) == 2:
                            row["Image2_file_name"] = Path(specimen.occurrences[1]).stem

                            logging.info(
                                "Recorded specimen, assigned {}: catalogNumber: {}, Image_1_file_name: {}, Image2_file_name: {}".format(
                                    row["Bombycoid_UI"],
                                    catalogNumber,
                                    Path(specimen.occurrences[0]).stem,
                                    Path(specimen.occurrences[1]).stem,
                                )
                            )
                        else:
                            logging.info(
                                "Recorded specimen, assigned {}: catalogNumber: {}, Image_1_file_name: {}".format(
                                    row["Bombycoid_UI"],
                                    catalogNumber,
                                    Path(specimen.occurrences[0]).stem,
                                )
                            )

                    needs_new_row = False

            if len(matches) > 0 and needs_new_row:
                template = matches[0].copy()

                new_row = reset_row(template)

                new_row["catalogNumber"] = catalogNumber

                if len(specimen.occurrences) > 0:
                    new_row["Image1_file_name"] = Path(specimen.occurrences[0]).stem

                    if len(specimen.occurrences) == 2:
                        new_row["Image2_file_name"] = Path(specimen.occurrences[1]).stem

                        logging.info(
                            "Recorded specimen with new row, assigned {}: catalogNumber: {}, Image_1_file_name: {}, Image2_file_name: {}".format(
                                new_row["Bombycoid_UI"],
                                catalogNumber,
                                Path(specimen.occurrences[0]).stem,
                                Path(specimen.occurrences[1]).stem,
                            )
                        )
                    else:
                        logging.info(
                            "Recorded specimen with new row, assigned {}: catalogNumber: {}, Image_1_file_name: {}".format(
                                new_row["Bombycoid_UI"],
                                catalogNumber,
                                Path(specimen.occurrences[0]).stem,
                            )
                        )

                df_dict.append(new_row)

        return pd.DataFrame.from_records(df_dict).sort_values(by="Bombycoid_UI")

    def run(self):
        print("loading in target worksheet:", self.worksheet, end="...")

        drive_sheet = self.gconnection.document.worksheet(self.worksheet)

        print("loaded!")

        print("converting to pandas dataframe...", end="")
        df = pd.DataFrame(drive_sheet.get_all_records())
        print("converted!\n")

        self.init_dict()

        self.find_in_fs()

        new_df = self.iter_specimen(df)

        new_df.to_csv("test.csv")

        new_sheet = self.gconnection.document.add_worksheet(
            drive_sheet.title + "_UPDATED", len(new_df.index), len(new_df.columns)
        )

        new_sheet.update([new_df.columns.values.tolist()] + new_df.values.tolist())


# TESTING GC FUNCTIONS, KEEPING FOR NOW FOR REFERENCE

# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html

# https://pythonexamples.org/pandas-dataframe-add-append-row/


def cli():
    my_parser = argparse.ArgumentParser(
        description="Populate a remote Google Sheet with specimen that match a set of requirements given a CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
          Example Runs:
            python3 ./wrangler.py --start_dir /fake/path --csv_file /path/to/file.csv --config ./config.json --sheet_id 1IIAp5sDSq61x1ZRmtbtcOSXoJ0QglJtilI6M6gUY3Dw\n
            python3 ./wrangler.py --start_dir /fake/path --csv_file /path/to/file.csv --config ./config.json --sheet_url https://docs.google.com/spreadsheets/d/1IIAp5sDSq61x1ZRmtbtcOSXoJ0QglJtilI6M6gUY3Dw/edit#gid=1483107405
         """
        ),
    )

    my_parser.add_argument(
        "-d",
        "--start_dir",
        required=True,
        type=str,
        help="path to the starting directory (MUST be a directory containing FAMILY subdirectories)",
    )
    my_parser.add_argument(
        "-c", "--config", action="store", required=True, help="path to the config.json"
    )

    my_parser.add_argument(
        "-w",
        "--worksheet",
        action="store",
        required=True,
        help="name of the tab worksheet in drive",
    )

    my_parser.add_argument(
        "-n",
        "--narrow",
        action="store",
        nargs="+",
        help="Look for only specific family folders",
    )

    group_files = my_parser.add_mutually_exclusive_group(required=True)
    group_files.add_argument(
        "-f", "--csv_file", action="store", help="path to CSV of specimen data"
    )
    group_files.add_argument(
        "-e", "--excel_file", action="store", help="path to XLSX of specimen data"
    )

    group = my_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--sheet_id",
        action="store",
        help="the ID extracted from the URL of the Google Sheet document",
    )
    group.add_argument(
        "-u",
        "--sheet_url",
        action="store",
        help="the full URL of the Google Sheet document",
    )

    args = my_parser.parse_args()

    start_dir = args.start_dir
    csv_file = args.csv_file
    worksheet = args.worksheet
    narrow = args.narrow
    excel_file = args.excel_file
    config = args.config
    sheet_id = args.sheet_id
    sheet_url = args.sheet_url

    print("Program starting...\n")

    wrangler = Wrangler(
        start_dir, config, excel_file, csv_file, sheet_id, sheet_url, worksheet, narrow
    )

    wrangler.run()
    print("\nAll computations completed...")


if __name__ == "__main__":
    cli()

# CURRENT TESTING
# python3 wrangler.py --start_dir . --config config.json -e ../testing/wrangler/test.xlsx -u https://docs.google.com/spreadsheets/d/12hPliU-tWEdrd9xxCEU7AW9s1O_D9wd5cTiwkKL1ZYE/edit#gid=515948364 -w MGCL_Image_IDs
# python3 wrangler.py --start_dir /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/PINNED_COLLECTION/IMAGES_UPLOADED/IMAGES_UPLOADED_NAMED --config config.json -f ../testing/wrangler/test.csv -u https://docs.google.com/spreadsheets/d/12hPliU-tWEdrd9xxCEU7AW9s1O_D9wd5cTiwkKL1ZYE/edit#gid=515948364 -w MGCL_Image_IDs
#

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

Insert images 1, 2 in row. Any additionals get added/appended as new row.
"""
