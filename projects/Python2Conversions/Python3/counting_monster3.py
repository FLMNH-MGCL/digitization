#!/usr/bin/env python

# >ident_seqname\nsequence\n   --> TEMPLATE FOR .fa .fasta

import os
import sys
import argparse
import re
from collections import defaultdict
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

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_sort(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


class Sequence:
    def __init__(self, name: str, sequence: str):
        self._name = name
        self._sequence = sequence

    @property
    def name(self):
        return self._name

class Monster:
    def __init__(self, file: str, outfile: str, delim: str):
        self._file = file
        self._outfile = outfile
        self._delim = delim
        self._identifiers = []

        # { seq_name : { identifier : count } }
        self._sequence_counts = {}

    def write_out(self):
        pass



    def collect(self):
        print("Collecting data from file...")
        with open(self._file, "r") as f:
            while True:
                seq_name = f.readline()

                if not seq_name:
                    break

                identifier = re.search(r"\>(.*?)\_", seq_name).group(1)

                if identifier and identifier not in self._identifiers:
                    self._identifiers.append(identifier)

                seq_name = re.sub(r"\>.*?\_", "", seq_name).replace("__comp0", "").strip()

                # this data goes unused as far as I know for this script
                sequence_data = f.readline()
                sequence = Sequence(seq_name, sequence_data)

                if sequence.name in self._sequence_counts:
                    identifier_count = self._sequence_counts[sequence.name]
                    if identifier in identifier_count:
                        identifier_count[identifier] += 1
                    else:
                        identifier_count[identifier] = 1

                else:
                    identifier_count = {}
                    identifier_count[identifier] = 1
                    self._sequence_counts[sequence.name] = identifier_count

        self._identifiers.sort(key=natural_sort)

                
    def count(self):
        self.collect()
        print("Data collected, counting now...")

        identifier_totals = defaultdict(lambda:0)

        with open(self._outfile, "w") as f:
            f.write("\t")
            for identifier in self._identifiers:
                f.write(identifier + "\t")
            f.write("\n")


            for sequence,identifier_count in self._sequence_counts.items():
                total = 0
                f.write(sequence + "\t")
                sorted_counts = sorted(identifier_count.keys())

                for identifier in self._identifiers:
                    if identifier in sorted_counts:
                        identifier_totals[identifier] += 1
                        total += identifier_count[identifier]
                        f.write(str(identifier_count[identifier]) + "\t")
                    else:
                        f.write(str(0) + "\t")
                        
                f.write(str(total) + "\n")

            f.write("\t")
            for identifier in self._identifiers:
                f.write(str(identifier_totals[identifier]) + "\t")
        
        print("Finished. Output written to {}".format(self._outfile))



def yesOrNo():
    prompt = "Would you like to continue?"

    print(prompt)
    while True:
        print("[1]. Yes")
        print("[2]. No")
        resp = input("--> ")

        if resp.lower() in ["yes", "y", "1"]:
            return True
        elif resp.lower() in ["no","n", "2"]:
            return False
        
        print("\nInvalid option!")
        print(prompt)


def main():
    my_parser = argparse.ArgumentParser(description="Parse fa and fasta files to get a count of sequences and their respective idententifiers. Will output in TSV format")
    my_parser.add_argument('-f', '--file', required=True, type=str, help="path to the file")
    my_parser.add_argument('-o', '--outfile', required=True, type=str, help="path to the output file (include desired name)")
    my_parser.add_argument('-d', '--delim', required=False, type=str, default="_", help="the delimeter used in the file (defaults to _)")
    args = my_parser.parse_args()

    file_in = args.file
    outfile = args.outfile
    delim = args.delim


    if not os.path.exists(file_in):
        print("Error: file {} does not exist in the filesystem!".format(file_in))
        sys.exit(1)

    
    if not os.path.isfile(file_in):
        print("Error: file {} exists, however it is not detected to be a file!".format(file_in))
        sys.exit(1)


    if os.path.exists(outfile):
        if os.path.isfile(outfile):
            print("Warning: path {} already exists and will be overwritten.".format(file_in))
            should_continue = yesOrNo()
            if not should_continue:
                sys.exit(0)
            else: print()
        else:
            print("Error: path {} already exists and it is not detected to be a file!".format(file_in))



    counter = Monster(file_in, outfile, delim)
    counter.count()

    # generate_locus(file_in, delim)

    # print(file_in, delim)

if __name__ == "__main__":
    main()