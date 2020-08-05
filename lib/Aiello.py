import os
import pandas as pd
from shutil import copyfile
import time
import sys
from lib.Logger import Logger
from lib.Helpers import Helpers

class AielloProject:
    def __init__(self):
        self.csv_path = ""
        self.destination = ""
        self.target_directory = ""
        self.error_log = []
        self.raw_csv_data = None
        self.mgcl_nums = dict()
        self.logger = None

    def reset(self):
        self.csv_path = ""
        self.destination = ""
        self.target_directory = ""
        self.error_log = []
        self.raw_csv_data = None
        self.mgcl_nums = dict()
        self.logger = None

    def check(self):
        headers = self.raw_csv_data.columns.values
        if len(headers) != 4:
            print(
                "\nError: invalid CSV ile, detected error in column count. " 
                "While this may not cause issues in the event there are more headers than required, as "
                "a precaution the program will now exit."
            )
            sys.exit()
        
        print()
        correct_headers = ["genus","species","cat#","sex"]
        should_exit = False
        for header in headers:
            if header not in correct_headers:
                print(
                    "Error: unknown header {}. Please ensure the provided csv file consists of "
                    "{}".format(header,correct_headers)
                )
                should_exit = True
        
        if should_exit:
            sys.exit()

    def generate_name(self, found, item):
        ext = found.split('.')[1]
        viewarr = found.split('_')
        view = viewarr[len(viewarr) - 1]
        new_name = item['genus'].strip() + '_' + item['species'].strip() + '_' + item['cat#'].strip() + '_' + item['sex'].strip() + '_' + view
        # print(new_name)
        return new_name

    def handle_find(self, target, found, path, item):
        if "downscale" in found:
            print("\nSkipping downscaled image {}".format(target))
            return

        self.mgcl_nums[item['cat#'].strip()] = True

        new_name = self.generate_name(found, item)

        if os.path.exists(self.destination + new_name):
            print("\nFile {} already exists in destination (skipping copy)".format(new_name))
        else:
            print('\nCopying and moving {} as {} to {}'.format(found, new_name, self.destination))
            copyfile(path, self.destination + new_name)


    def find_item(self, path, item):
        target = item['cat#']
        if os.path.exists(path):
            for image in sorted(os.listdir(path)):
                if target in image:
                    self.handle_find(target, image, path + image, item)
        else:
            print("Error: path is not in filesystem (skipping entry)...\nInvalid path --> {}".format(path))

    def recursive_find_item(self, path, item):
        subdirs = Helpers.get_dirs(path)
        for subdir in subdirs:
            self.recursive_find_item(path + subdir + '/', item)
        self.find_item(path, item)

    def run(self):

        # define prompts
        target_prompt = "\nPlease input the path to the directory that contains the images: \n--> "
        destination_prompt = "\nPlease input the path you would like the copies to go: \n--> "
        csv_prompt = "\nPlease enter the path to the properly formatted CSV file: \n--> "

        print("### AIELLO PROGRAM ###")

        # get path for files
        self.target_directory = Helpers.get_existing_path(Helpers.path_prompt(target_prompt), True)
        # print("Obtained target directory: {}".format(self.target_directory))

        # get path for destination
        self.destination = Helpers.get_existing_path(Helpers.path_prompt(destination_prompt), True)
        # print("Obtained destination directory: {}".format(self.destination))


        # get csv path
        self.csv_path = Helpers.get_existing_path(Helpers.file_prompt(csv_prompt), False)
        # print("Obtained csv file: {}".format(self.csv_path))


        # parse csv
        self.raw_csv_data = pd.read_csv(self.csv_path, header=0)
        # print(self.raw_csv_data)

        self.check()

        # initialize the dict
        for id,item in self.raw_csv_data.iterrows():
            self.mgcl_nums[item['cat#'].strip()] = False

        print("Finding items...")

        # find items
        for id,item in self.raw_csv_data.iterrows():
            self.recursive_find_item(self.target_directory + item['genus'].strip() + '/', item)

        for mgcl_num in self.mgcl_nums:
            if not self.mgcl_nums[mgcl_num]:
                print('{} could not be located.'.format(mgcl_num))

        print()
        self.reset()