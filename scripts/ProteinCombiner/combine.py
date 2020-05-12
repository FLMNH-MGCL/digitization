#!/usr/bin/env python
import os
import datetime
import sys
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

valid_files = ["fa", "fasta"]

# next few helper functions taken from my Helpers class used in Digitization.py
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

def path_prompt(prompt):
    path = input(prompt)
    path = path.strip()
    path = path.replace('\\', '/')

    if not path.endswith('/'):
        path += '/'

    return path

def get_folders(path):
    dirs = []
    for dir in sorted(os.listdir(path)):
        if os.path.isdir(path + dir):
            dirs.append(dir)
    return dirs

def get_files(path):
    files = []
    for f in sorted(os.listdir(path)):
        if os.path.isfile(path + f):
            files.append(f)
    return files

class Combiner:
    def __init__(self, target_folder):
        self.buffer = ""
        self.target_folder = target_folder

    def write_out(self):
        print(self.buffer)
        filename = "combined.txt"
        with open(self.target_folder + filename, "w") as file:
            file.write(self.buffer)

    def os_walk(self, path):
        folders = get_folders(path)
        files = get_files(path)

        for folder in folders:
            self.os_walk(path + folder + "/")
        
        for f in files:
            extension = f.split(".")
            if len(extension) > 1 and extension[1] in valid_files:
                with open(path + f, 'r') as file:
                    data = file.read()
                    self.buffer += data + "\n\n"
        
            self.buffer += "\n"

    def run(self):
        self.os_walk(self.target_folder)

def help():
  help_str = str(
    "File Combiner Program\n"
    "Aaron Leopold <aaronleopold1221@gmail.com>\n"
    "Command line tools created for the FLMNH\n\n"
    "USAGE:\n"
    "   combine.py [option]\n\n"
    "OPTIONS:\n"
    "   -h, --help              Prints help information\n"
    "DEFAULT BEHAVIOR:\n"
    "   Combines every protein / nucleotide file into one master file"
  )

  print(help_str)
  # input("Press enter to exit...")

def main():
    # get args
    argument_list = sys.argv
    arg_len = len(argument_list)
    
    if arg_len == 2 and argument_list[1] in ["-h", "--help"]:
        # display help
        help()
        getch()
    elif arg_len == 1:
        # run program
        target_folder = path_prompt("Please enter the path to the parent folder:\n --> ")
        target_folder = get_existing_path(target_folder, True)
        combiner = Combiner(target_folder)
        combiner.run()
        combiner.write_out()
    else:
        print(
            "Incorrect usage. Please run with the help flag for more usage information:\n"
            "   combine.py --help\n"
        )



if __name__ == "__main__":
    main()