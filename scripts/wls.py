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


valid_files = ["JPG", "jpg", "CR2", "cr2", "PNG", "png"]


class WLS:
    def __init__(self, method=""):
        # str array unless unique, then array of dictionaries
        self.data = []
        self.target_directory = os.getcwd() + "/"
        self.method = method
        self.filter = None

    def set_filter(self, filter):
        self.filter = filter

    def generate_log_arr(self):
        csv_data = []
        if self.method == "":
            # loop through self.data
            return self.data

        elif self.method == "unique":
            # loop through self.data
            # each index is dir data
            for dir in self.data:
                for f in dir:
                    csv_data.append(f + "\n")
                csv_data.append("\n")

        elif self.method == "views":
            # print(self.data)
            for _map in self.data:
                csv_data.append(_map["PATH"] + "\n")
                for key in _map:
                    if key != "PATH":
                        for image in _map[key]:
                            csv_data.append(image + ",")
                        csv_data.append("\n")
                csv_data.append("\n")

        else:
            # this should never get here
            print("Error generating log file... Please retry program...")

        return csv_data

    def write_out(self):
        d = datetime.datetime.today()
        date = str(d.year) + "_" + str(d.month) + "_" + str(d.day)
        filename = self.target_directory + "WLS_SCRIPT_LOG_" + date
        csv_data = self.generate_log_arr()

        count = ""
        num = 0
        while os.path.exists(filename + count + ".csv"):
            if num == 0:
                filename += "_"
            num += 1
            count = str(num)

        if num == 0:
            filename = filename + ".csv"
        else:
            filename = filename + count + ".csv"

        csv_file = open(filename, mode="w")
        for data in csv_data:
            csv_file.write(data)
        csv_file.close()

    def get_folders(self, path):
        dirs = []
        for dir in sorted(os.listdir(path)):
            if os.path.isdir(path + dir):
                dirs.append(dir)
        return dirs

    def get_files(self, path):
        global valid_files
        files = []
        for file in sorted(os.listdir(path)):
            if os.path.isfile(path + file):
                if (len(file.split(".")) > 1) and (file.split(".")[1] in valid_files):
                    if self.filter is None:
                        files.append(file)
                    elif self.filter in file:
                        files.append(file)
        return files

    def parse_name(self, name):
        new_name = ""
        name_vec = name.split("_")

        if len(name_vec) > 2:
            new_name = name_vec[0] + "_" + name_vec[1]
        else:
            new_name = name.split(".")[0]

        return new_name

    def run_views(self, path):
        files = self.get_files(path)
        dirs = self.get_folders(path)
        dir_map = dict()

        print("\nCurrently working in: {}".format(path))

        for dir in dirs:
            self.run_views(path + dir + "/")
        dir_map["PATH"] = path
        for file in files:
            mapped_name = self.parse_name(file)
            # print("Current file: {}\nParsed name: {}".format(file, mapped_name))
            if mapped_name in dir_map:
                dir_map[mapped_name].append(file)
            else:
                dir_map[mapped_name] = []
                dir_map[mapped_name].append(file)

        self.data.append(dir_map)

    def run_unique(self, path):
        files = self.get_files(path)
        dirs = self.get_folders(path)
        dir_arr = []

        for dir in dirs:
            self.run_unique(path + dir + "/")
        dir_arr.append(path)

        print("Currently working in: {}\n".format(path))
        for file in files:
            mapped_name = self.parse_name(file)
            # check if existing already for dir
            if not mapped_name in dir_arr:
                dir_arr.append(mapped_name)

        self.data.append(dir_arr)

    def run(self, path):
        files = self.get_files(path)
        dirs = self.get_folders(path)

        for dir in dirs:
            self.run(path + dir + "/")
        self.data.append(path + "\n")
        print("Currently working in: {}\n".format(path))
        for file in files:
            self.data.append(file + "\n")
        self.data.append("\n")


def help():
    help_str = str(
        "WLS Program\n"
        "Aaron Leopold <aaronleopold1221@gmail.com>\n"
        "Command line tools created for the FLMNH\n\n"
        "USAGE:\n"
        "   wls.py [option] [filter]\n\n"
        "OPTIONS:\n"
        "   -h, --help              Prints help information\n"
        "   -u, --unique-only       Run WLS only logging unique files\n"
        "   -sv, --separate-views   Run WLS separating different specimen views into separate columns\n\n"
        "FILTER:\n"
        "   -f, --filter            Will use filter to generate dataset\n"
        "   example: wls.py --filter myWord\n"
    )

    print(help_str)
    # input("Press enter to exit...")


def extract_filter(argument_list, arg_len):
    if arg_len < 3:
        return "OK", None

    elif arg_len == 3:
        if argument_list[1] in ["--filter", "-f"]:
            return "OK", argument_list[2]
        else:
            # invalid usage here
            # if isnt filter at pos 1, then arg len is invalid usage
            return "BAD", None

    elif arg_len == 4:
        if argument_list[2] in ["--filter", "-f"]:
            return "OK", argument_list[3]
        else:
            return "BAD", None

    else:
        return "BAD", None


def main():
    argument_list = sys.argv
    arg_len = len(argument_list)
    filter = extract_filter(argument_list, arg_len)

    if filter[0] == "BAD":
        print(
            "Incorrect usage. Please run with the help flag for more usage information:\n"
            "   wls.py --help\n"
        )
    else:
        filter = filter[1]

    if arg_len == 1:
        # run normal wls
        program = WLS()
        program.set_filter(None)
        program.run(program.target_directory)
        program.write_out()

    elif arg_len > 1 and arg_len < 5:
        # parse argument
        target_program = argument_list[1]

        if target_program in ["--help", "-h"]:
            help()
            getch()

        elif target_program in ["--unique-only", "-u"]:
            program = WLS("unique")
            program.set_filter(filter)
            program.run_unique(program.target_directory)
            program.write_out()

        elif target_program in ["--separate-views", "-sv"]:
            program = WLS("views")
            program.set_filter(filter)
            program.run_views(program.target_directory)
            program.write_out()

        elif target_program in ["--filter", "-f"]:
            # default wls run with filter
            if arg_len == 3:
                filter = argument_list[2]
                program = WLS()
                program.set_filter(filter)
                program.run(program.target_directory)
                program.write_out()
            else:
                # incorrect argument ordering (filter listed first)
                print(
                    "Incorrect argument ordering. Please run with the help flag for more usage information:\n"
                    "   wls.py --help\n"
                )

        else:
            # unknown option
            print("Unknown usage.")

        # input("Press enter to exit...")


if __name__ == "__main__":
    main()