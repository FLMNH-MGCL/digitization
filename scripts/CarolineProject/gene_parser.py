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


class GeneParser:
    valid_gene_files = ["fa", "fasta"]
    valid_csv_files = "csv"

    def __init__(self, gene_file="", csv_file=""):
        self.gene_file = gene_file
        self.csv_file = csv_file
        self.raw_csv_data = None
        self.genes = []

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
        while not os.path.exists(correct_path) or (is_dir and not os.path.isdir(correct_path)) or (not is_dir and os.path.isdir(correct_path)):
            print("\nCould not find path / file in filesystem (or is wrong type, i.e. requires file but provided directory)...")
            correct_path = input('\nPlease input an appropriate path: \n --> ')
            correct_path = correct_path.strip()

            if is_dir:
                if not correct_path.endswith('/') or not correct_path.endswith('\\'):
                    correct_path += '/'
            else:
                if correct_path.endswith('/'):
                    correct_path = correct_path[:-1]

                elif correct_path.endswith('\\'):
                    correct_path = correct_path[:-2]

        return correct_path

    @staticmethod
    def path_prompt(prompt, is_dir):
        path = input(prompt)
        path = path.strip()
        path = path.replace('\\', '/')

        if not path.endswith('/') and is_dir:
            path += '/'

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

    def collect_input(self):
        self.csv_file = GeneParser.get_existing_path(GeneParser.path_prompt("Please enter path to the csv file: \n--> ", False), False)
        self.gene_file = GeneParser.get_existing_path(GeneParser.path_prompt("Please enter path to the fa/fasta file: \n--> ", False), False)

    @staticmethod
    def parse_gene_header(gene_header):
        if type(gene_header) != str:
            print("error occurred... exiting")
            sys.exit()
        
        gene_header = gene_header.replace('>', '')
        header_comma = gene_header.split(',')

        try:
            # gene has version information
            if len(header_comma) == 2:
                header_first = header_comma[0].strip()
                header_second = header_comma[1].strip()

                acc_num = header_first.split(' ')[0]
                gname = header_first.split(' ')[1]
                # .replace(' ', '') --> csv data doesn't contain spaces
                version = header_second.split('[')[0].strip()
                associated_species = header_second.split('[')[1].replace(']', '')

                print("acc_num:", acc_num, "\ngname:", gname, "\nversion", version, "\nspecies", associated_species, "\n")
            
            elif len(header_comma) == 1:
                header_brackets = gene_header.split('[')
                header_first = header_brackets[0]
                associated_species = header_brackets[1].replace(']', '')

                acc_num = header_first.split(' ')[0]
                gname = header_first.split(' ')[1].strip()

                print("acc_num:", acc_num, "\ngname:", gname, "\nspecies", associated_species, "\n")
            else:
                print("Error: Unregocnized gene format!")
                print(gene_header)
        except:
            print("Uh oh... Something went wrong!")
            print(gene_header)
            sys.exit()

    
    def collect_gene_data(self):
        with open(self.gene_file, "r") as f:
            while True:
                header_line = f.readline()

                if not header_line:
                    break

                gene_line = f.readline()

                gene = tuple((header_line.strip(), gene_line.strip()))
                GeneParser.parse_gene_header(header_line.strip())
                self.genes.append(gene)



    def run(self):
        self.raw_csv_data = pd.read_csv(self.csv_file)
        # print(self.raw_csv_data)

        self.collect_gene_data()
        print()
        print(self.genes[0])

        return

        # loop through every row in csv
        for row in self.raw_csv_data.iterrows():
            index = row[0]
            row = row[1]
            print(row)

            qseqid = row['qseqid']
            gene = row['gene']

            break


def main():
    my_parser = argparse.ArgumentParser(description="Parse fa and fasta files to extract the accession number and gene name for each")
    my_parser.add_argument('--gene-file', required=False, type=str, help="path to the fa/fasta file", default=None)
    my_parser.add_argument('--csv-file', required=False,type=str, help="path to the csv file", default=None)
    args = my_parser.parse_args()

    gene_file=args.gene_file
    csv_file = args.csv_file

    if gene_file is None or csv_file is None:
        # default to program collecting input
        parser = GeneParser()
        parser.collect_input()
        parser.run()
    else:
        parser = GeneParser(gene_file=gene_file, csv_file=csv_file)
        parser.run()

    # print(gene_file, csv_file)

if __name__ == "__main__":
    main()