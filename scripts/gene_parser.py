import os
import sys
import argparse
import pandas as pd

# https://stackoverflow.com/questions/1394956/how-to-do-hit-any-key-in-python
try:
    # Win32
    from msvcrt import getch
except ImportError:
    # UNIX
    def getch():
        import sys, tty, termios

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        print("Press any key to exit...")
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


class Gene:
    def __init__(self, sseqid, gene, species, version=None):
        self.sseqid = sseqid
        self.gene = gene
        self.version = version
        self.species = species


class GeneParser:
    valid_gene_files = ["fa", "fasta"]
    valid_csv_files = "csv"

    def __init__(self, gene_file="", csv_file=None, excel_file=None):
        self.gene_file = gene_file

        if csv_file is None and excel_file is None:
            self.document = None
        elif csv_file is None and excel_file is not None:
            self.document = excel_file
            self.type = "excel"
        else:
            self.document = csv_file
            self.type = "csv"

        self.raw_data = None
        self.genes = []

    @staticmethod
    def check_valid_sources(filepath, ext):
        file_vec = os.path.basename(filepath).split(".")
        if len(file_vec) < 2:
            return False

        passed_ext = file_vec[1]

        if ext != passed_ext.lower():
            return False

        return True

    @staticmethod
    def help():
        help_str = str(
            "Gene Parser Program\n"
            "Aaron Leopold <aaronleopold1221@gmail.com>\n"
            "Command line tools created for the FLMNH\n\n"
            "USAGE:\n"
            "   gene_parser.py [args] | [option]\n\n"
            "ARGS:\n"
            "   -c, --csv-file"
            "OPTIONS:\n"
            "   -h, --help              Prints help information\n"
            "DEFAULT BEHAVIOR:\n"
            "   Combines every protein / nucleotide file into one master file"
        )

        print(help_str)

    # next few helper functions taken from my Helpers class used in Digitization.py
    @staticmethod
    def get_existing_path(path, is_dir):
        correct_path = path
        while (
            not os.path.exists(correct_path)
            or (is_dir and not os.path.isdir(correct_path))
            or (not is_dir and os.path.isdir(correct_path))
        ):
            print(
                "\nCould not find path / file in filesystem (or is wrong type, i.e. requires file but provided directory)..."
            )
            correct_path = input("\nPlease input an appropriate path: \n --> ")
            correct_path = correct_path.strip()

            if is_dir:
                if not correct_path.endswith("/") or not correct_path.endswith("\\"):
                    correct_path += "/"
            else:
                if correct_path.endswith("/"):
                    correct_path = correct_path[:-1]

                elif correct_path.endswith("\\"):
                    correct_path = correct_path[:-2]

        return correct_path

    @staticmethod
    def path_prompt(prompt, is_dir):
        path = input(prompt)
        path = path.strip()
        path = path.replace("\\", "/")

        if not path.endswith("/") and is_dir:
            path += "/"

        return path

    @staticmethod
    def get_folders(path):
        dirs = []
        for dir in sorted(os.listdir(path)):
            if os.path.isdir(path + dir):
                dirs.append(dir)
        return dirs

    @staticmethod
    def get_files(path):
        files = []
        for f in sorted(os.listdir(path)):
            if os.path.isfile(path + f):
                files.append(f)
        return files

    # TODO: add options to select csv or excel
    def collect_input(self):
        self.csv_file = GeneParser.get_existing_path(
            GeneParser.path_prompt("Please enter path to the csv file: \n--> ", False),
            False,
        )
        self.gene_file = GeneParser.get_existing_path(
            GeneParser.path_prompt(
                "Please enter path to the fa/fasta file: \n--> ", False
            ),
            False,
        )

    @staticmethod
    def parse_gene_header(gene_header):
        if type(gene_header) != str:
            print("error occurred... exiting")
            sys.exit()

        gene_header = gene_header.replace(">", "")
        header_comma = gene_header.split(",")
        genes = None

        try:
            # gene has version information
            if len(header_comma) == 2:
                header_first = header_comma[0].strip()
                header_second = header_comma[1].strip()

                acc_num = header_first.split(" ")[0]
                gname = header_first.split(" ")[1]
                # .replace(' ', '') --> csv data doesn't contain spaces
                version = header_second.split("[")[0].strip()
                associated_species = header_second.split("[")[1].replace("]", "")

                # print("acc_num:", acc_num, "\ngname:", gname, "\nversion", version, "\nspecies", associated_species, "\n")

                gene = Gene(acc_num, gname, associated_species, version)
                return gene

            elif len(header_comma) == 1:
                header_brackets = gene_header.split("[")
                header_first = header_brackets[0]
                associated_species = header_brackets[1].replace("]", "")

                acc_num = header_first.split(" ")[0]
                gname = header_first.split(" ")[1].strip()

                # print("acc_num:", acc_num, "\ngname:", gname, "\nspecies", associated_species, "\n")

                gene = Gene(acc_num, gname, associated_species)
                return gene
                # genes.append(gene)
            else:
                print("Error: Unregocnized gene format!")
                # TODO: extract acc_num
                # dump to a col in csv saying sm about invalid format
                print(gene_header, "\n")
                return None
        except:
            print("Uh oh... Something went wrong!")
            print(gene_header)
            sys.exit()

        return genes

    def collect_gene_data(self):
        print("Extracting gene data from .fa/.fasta file...\n")
        with open(self.gene_file, "r") as f:
            while True:
                header_line = f.readline()

                if not header_line:
                    break

                # gene_line = f.readline()

                # gene = tuple((header_line.strip(), gene_line.strip()))
                gene = GeneParser.parse_gene_header(header_line.strip())
                self.genes.append(gene)

    def insert_new_col(self):
        print("Creating two new columns if they do not already exist...")
        columns = self.raw_data.columns
        if "gname" in columns and "version" in columns:
            return

        if "gname" not in columns:
            # get index of sseqid
            left_index = columns.get_loc("sseqid")
            self.raw_data.insert(
                left_index + 1, "gname", ["" for i in range(self.raw_data.shape[0])]
            )
            columns = self.raw_data.columns
            print("created 'gname'...")

        if "version" not in columns:
            # get index of gname
            left_index = columns.get_loc("gname")
            self.raw_data.insert(
                left_index + 1, "version", ["" for i in range(self.raw_data.shape[0])]
            )
            print("created 'version'...")

        print()

    def find_and_insert(self, gene):
        sseqid = gene.sseqid

        instances = self.raw_data[self.raw_data["sseqid"] == sseqid].index.tolist()

        if len(instances) == 0:
            print("No matches found for {}...".format(sseqid))
            return
        else:
            print(
                "{} matches found for {}, inserting now...".format(
                    len(instances), sseqid
                )
            )

        for instance in instances:
            self.raw_data.at[instance, "gname"] = gene.gene

            if gene.version is not None:
                self.raw_data.at[instance, "version"] = gene.version

    def run(self):
        self.raw_data = None

        if self.type == "csv":
            self.raw_data = pd.read_csv(self.document)
        else:
            self.raw_data = pd.read_excel(self.document)

        self.collect_gene_data()
        self.insert_new_col()
        print("Finding matches and inserting into csv...\n")

        for gene in self.genes:
            if gene is None:
                continue
            self.find_and_insert(gene)

        self.raw_data.to_csv("test.csv")


def main():
    my_parser = argparse.ArgumentParser(
        description="Parse fa and fasta files to extract the accession number and gene name for each"
    )
    my_parser.add_argument(
        "--gene-file",
        required=False,
        type=str,
        help="path to the fa/fasta file",
        default=None,
    )
    my_parser.add_argument(
        "--csv-file",
        required=False,
        type=str,
        help="path to the csv file",
        default=None,
    )
    my_parser.add_argument(
        "--excel-file",
        required=False,
        type=str,
        help="path to the excel file",
        default=None,
    )
    args = my_parser.parse_args()

    gene_file = args.gene_file
    csv_file = args.csv_file
    excel_file = args.excel_file

    if gene_file is None or (csv_file is None and excel_file is None):
        # default to program collecting input
        parser = GeneParser()
        parser.collect_input()
        parser.run()
    elif excel_file is not None and csv_file is not None:
        print(
            "\nError. You input two source files of two different types. \nPlease select one and rerun the program with the single selection only.\n"
        )
    elif csv_file is not None:
        GeneParser.check_valid_sources(csv_file, "csv")
        parser = GeneParser(gene_file=gene_file, csv_file=csv_file)
        parser.run()
    elif excel_file is not None:
        GeneParser.check_valid_sources(excel_file, "xlsx")
        parser = GeneParser(gene_file=gene_file, csv_file=csv_file)
        parser.run()
    else:
        print(
            "\nError. Invalid startup configuration, exiting program. Please run with the help flag to review usage.\n"
        )

    # print(gene_file, csv_file)


if __name__ == "__main__":
    main()

"""
TESTING SHELL SCRIPTS

python3 gene_parser.py --gene-file /Users/aaronleopold/Documents/museum/gene/AllDrosHearingGenes_AA.fa --csv-file /Users/aaronleopold/Documents/museum/gene/DrosHearingGenes_AA_blastp_DmOnly_SANDBOX/blastp.csv

python3 gene_parser.py --gene-file /Users/aaronleopold/Documents/museum/gene/AllDrosHearingGenes_AA.fa --csv-file /Users/aaronleopold/Documents/museum/gene/DrosHearingGenes_AA_blastp_DmOnly_SANDBOX/blastp.csv --excel-file TEST
"""