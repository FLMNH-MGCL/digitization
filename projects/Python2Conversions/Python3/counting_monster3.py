#!/usr/bin/env python

import os
import sys
import argparse
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

def generate_locus(file_in: str, delim: str) -> [str]:
    locus_list = []

    with open(file_in, "r") as f:
        line = f.readline()
        while line:
            if line[0] == ">":
                linesplit = line.strip(">").strip().split(delim)
                locus = linesplit[0]
                locus_list.append(locus)
                line = f.readline()
            else:
                line = f.readline()
    
    # cast to set to remove duplicates, then cast back to list
    return list(set(locus_list))

def generate_identifiers(locus_list: [str]):
    identifier_lists = dict()
    count_list = [0]*len(locus_list) # don't know what this is used for yet

def main():
    my_parser = argparse.ArgumentParser(description="Parse fa and fasta files to extract the accession number and gene name for each")
    my_parser.add_argument('-f', '--file', required=True, type=str, help="path to the file")
    my_parser.add_argument('-d', '--delim', required=True, type=str, help="the delimeter used in the file")
    args = my_parser.parse_args()

    file_in = args.file
    delim = args.delim

    generate_locus(file_in, delim)
    # print(file_in, delim)

if __name__ == "__main__":
    main()