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
from datetime import datetime
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


# TODO: scan_id ??
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
        scan_id,
    ):
        self.bomb_id = None
        self.catalog_number = catalog_number
        self.other_catalog_numbers = other_catalog_numbers
        self.family = family
        self.sci_name = sci_name
        self.genus = genus
        self.spec_epithet = spec_epithet
        self.record_id = record_id
        self.references = references
        self.scan_id = scan_id

        self.occurrences = []

    def __str__(self):
        return "\tbombID: {},\n\tcatalogNumber: {},\n\totherCatalogNumber: {},\n\tfamily: {},\n\tgenus: {},\n\tsepcies: {},\n\trecordId: {},\n\trefs: {},\n\toccurrences: {}".format(
            self.bomb_id,
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
        file,
        sheet_id,
        sheet_url,
        worksheet,
        narrow,
    ):
        if sheet_url is not None:
            self.gconnection = GDriveConnector(None, sheet_url, config_location)

        else:
            self.gconnection = GDriveConnector(sheet_id, None, config_location)

        self.file = file
        self.raw_data = Wrangler.parse_file(self.file)

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
    def parse_file(file_path):
        """
        Attempts to parse CSV or Excel data of specimen

        :param file_path: The os path str to the CSV file
        :type file_path: str

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

        # there are two separate functions for pandas to read either a CSV or XLSX,
        # but the return of each is the same DataFrame type.
        if ext.lower() == "csv":
            return pd.read_csv(file_path)
        elif ext.lower() == "xlsx":
            try:
                return pd.read_excel(file_path)
            except Exception:
                return pd.read_excel(file_path, engine="openpyxl")
        else:
            # this error logically should not ever be hit, because of the extension
            # check above, however I added it for safety.
            error_message(
                "Invalid file provided: expected .csv or .xlsx, recieved {}".format(
                    ext.lower()
                )
            )

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
        except Exception:
            # not on windows, no need to worry about this
            family_genus = family_genus.group()

        family_genus_vec = family_genus.split("/")

        if len(family_genus_vec) < 2:
            return None

        return family_genus_vec

    @staticmethod
    def create_new_ws(connection, current_ws, df):
        now = datetime.now()
        time = now.strftime("%m-%d-%Y, %H:%M:%S")
        while True:
            suffix = "_UPDATED_{}".format(time)
            try:
                return connection.document.add_worksheet(
                    current_ws.title + suffix, len(df.index), len(df.columns)
                )
            except Exception:
                time = now.strftime("%m-%d-%Y (%H:%M:%S)")

    def collect_files(self):
        """
        Collects all image files, not marked as duplicates at and below the starting directory

        :rtype: list of str representing paths to images in fs
        """

        if self.narrow:
            print("narrow parameter used: will isolate folders accordingly...\n")

            globs = []
            for family in self.narrow:
                start_path = os.path.join(self.start_dir, family)

                print("collecting files for", family, "at", start_path, end="...")

                globs += glob.glob(
                    "{}/**/*.*".format(os.path.join(self.start_dir, family))
                )

                print("collected!")

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
                scan_id = None

                if "scan_id" in row:
                    scan_id = str(row["scan_id"])

                specimen = Specimen(
                    catalog_number,
                    other_catalog_numbers,
                    family,
                    sci_name,
                    genus,
                    spec_epithet,
                    record_id,
                    references,
                    scan_id,
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

    def check_for_match(self, file, catalog_number, family, genus):
        specimen = self.specimens[catalog_number]

        if not isinstance(specimen, Specimen):
            logging.warning(
                "Invalid specimen detected from csv/excel: {}".format(specimen)
            )

        # ignoring case, do the family and genus pairs match (i.e. are they the same)
        elif str_cmp(specimen.family, family) and str_cmp(specimen.genus, genus):
            # if they matched ignoring case but don't match when not ignoring case,
            # i send a warning in the log. This is not breaking, however warrants at the
            # very least a warning.
            if not str_cmp(specimen.family, family, False) or not str_cmp(
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
            specimen.occurrences.append(file)
            logging.info(
                "Appended {} to list of occurrences @ {}...".format(
                    catalog_number, file
                )
            )

        else:
            # log this, found MGCL number but information differs about its
            # data than what was extracted from CSV
            logging.warning(
                "Found {} @ {} - information differs about its data than what was extracted from csv/xlsx...\nExpected Family,Genus: {},{}\nFound: {},{}".format(
                    catalog_number,
                    file,
                    family,
                    genus,
                    specimen.family,
                    specimen.genus,
                )
            )

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
                self.check_for_match(f, catalog_number, family, genus)

    def _handle_alter_row(self, row, catalog_number, specimen):
        row["catalogNumber"] = catalog_number

        if len(specimen.occurrences) > 0:
            row["Image1_file_name"] = Path(specimen.occurrences[0]).stem

            if len(specimen.occurrences) == 2:
                row["Image2_file_name"] = Path(specimen.occurrences[1]).stem

                logging.info(
                    "Recorded specimen, assigned {}: catalogNumber: {}, Image_1_file_name: {}, Image2_file_name: {}".format(
                        row["Bombycoid_UI"],
                        catalog_number,
                        Path(specimen.occurrences[0]).stem,
                        Path(specimen.occurrences[1]).stem,
                    )
                )
            else:
                logging.info(
                    "Recorded specimen, assigned {}: catalogNumber: {}, Image_1_file_name: {}".format(
                        row["Bombycoid_UI"],
                        catalog_number,
                        Path(specimen.occurrences[0]).stem,
                    )
                )

    def _handle_insert_row(self, new_row, catalog_number, specimen, df):
        new_row["catalogNumber"] = catalog_number
        new_row["recordId"] = specimen.record_id
        new_row["references"] = specimen.references
        new_row["scientificName"] = specimen.sci_name

        if "scan_id" in new_row:
            new_row["scan_id"] = specimen.scan_id

        if len(specimen.occurrences) > 0:
            new_row["Image1_file_name"] = Path(specimen.occurrences[0]).stem

            if len(specimen.occurrences) == 2:
                new_row["Image2_file_name"] = Path(specimen.occurrences[1]).stem

                logging.info(
                    "Recorded specimen with new row, assigned {}: catalogNumber: {}, Image_1_file_name: {}, Image2_file_name: {}".format(
                        new_row["Bombycoid_UI"],
                        catalog_number,
                        Path(specimen.occurrences[0]).stem,
                        Path(specimen.occurrences[1]).stem,
                    )
                )
            else:
                logging.info(
                    "Recorded specimen with new row, assigned {}: catalogNumber: {}, Image_1_file_name: {}".format(
                        new_row["Bombycoid_UI"],
                        catalog_number,
                        Path(specimen.occurrences[0]).stem,
                    )
                )

        df.append(new_row)

    def _iter_matched_rows(self, rows, catalog_number, specimen):

        needs_new_row = True

        for row in rows:
            if (
                row["catalogNumber"]
                or row["Image1_file_name"]
                or row["Image2_file_name"]
            ):
                continue

            else:
                self._handle_alter_row(row, catalog_number, specimen)

                needs_new_row = False

                row["recordId"] = specimen.record_id
                row["references"] = specimen.references
                row["scientificName"] = specimen.sci_name

                if "scan_id" in row:
                    row["scan_id"] = specimen.scan_id

        return needs_new_row

    def iter_specimen(self, df):

        df_dict = df.to_dict("records")

        for catalog_number, specimen in self.specimens.items():
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

            needs_new_row = self._iter_matched_rows(matches, catalog_number, specimen)

            if len(matches) > 0 and needs_new_row:
                template = matches[0].copy()

                new_row = reset_row(template)

                self._handle_insert_row(new_row, catalog_number, specimen, df_dict)

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

        new_sheet = Wrangler.create_new_ws(self.gconnection, drive_sheet, new_df)

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
            python3 ./wrangler.py --start_dir /fake/path --file /path/to/file.csv --config ./config.json --sheet_id 1IIAp5sDSq61x1ZRmtbtcOSXoJ0QglJtilI6M6gUY3Dw\n
            python3 ./wrangler.py --start_dir /fake/path --file /path/to/file.csv --config ./config.json --sheet_url https://docs.google.com/spreadsheets/d/1IIAp5sDSq61x1ZRmtbtcOSXoJ0QglJtilI6M6gUY3Dw/edit#gid=1483107405
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

    # group_files = my_parser.add_mutually_exclusive_group(required=True)
    # group_files.add_argument(
    #     "-f", "--csv_file", action="store", help="path to CSV of specimen data"
    # )
    # group_files.add_argument(
    #     "-e", "--excel_file", action="store", help="path to XLSX of specimen data"
    # )

    my_parser.add_argument(
        "-f", "--file", action="store", help="path to csv/xlsx of specimen data"
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
    worksheet = args.worksheet
    narrow = args.narrow
    _file = args.file
    config = args.config
    sheet_id = args.sheet_id
    sheet_url = args.sheet_url

    print("Program starting...\n")

    wrangler = Wrangler(
        start_dir, config, _file, sheet_id, sheet_url, worksheet, narrow
    )

    wrangler.run()

    print("\nAll computations completed...")
    print(
        "Log may be found at {}".format(
            os.path.join(wrangler.start_dir, "wrangler.log")
        )
    )


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
    specimen obj: { bomb_id, catalogNumber, otherCatalogNumber, family, genus, sepcies, recordId, refs, location_obj }
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
    if get UI -> assign object bomb_id

Insert images 1, 2 in row. Any additionals get added/appended as new row.

python3 wrangler.py --start_dir /Volumes/flmnh/NaturalHistory/Lepidoptera/Kawahara/Digitization/LepNet/PINNED_COLLECTION/IMAGES_UPLOADED/IMAGES_UPLOADED_NAMED --config config.json -f ../testing/wrangler/Bombycoidea_5.xlsx -u https://docs.google.com/spreadsheets/d/12hPliU-tWEdrd9xxCEU7AW9s1O_D9wd5cTiwkKL1ZYE/edit#gid=515948364 -w MGCL_Image_IDs --narrow Apatelodidae Bombycidae
"""
