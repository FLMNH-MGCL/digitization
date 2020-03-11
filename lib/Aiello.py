import os
import pandas as pd
from shutil import copyfile
import time
from lib.Logger import Logger
from lib.Helpers import Helpers

old_new_paths = []
mgcl_nums = dict()
destination = ''
error_log = []

class AielloProject:
    def __init__(self):
        self.csv_path = ""
        self.destination = ""
        self.target_directory = ""
        self.error_log = []
        self.raw_csv_data = None
        self.mgcl_nums = dict()
        self.logger = None

    def generate_name(self, found, item):
        ext = found.split('.')[1]
        viewarr = found.split('_')
        view = viewarr[len(viewarr) - 1]
        new_name = item['Genus'].strip() + '_' + item['species'].strip() + '_' + item['cat#'].strip() + '_' + item['sex'].strip() + '_' + view
        # print(new_name)
        return new_name

    def handle_find(self, target, found, path, item):
        self.mgcl_nums[item['cat#'].strip()] = True

        new_name = self.generate_name(found, item)
        print('\nCopying and moving {} as {} to {}'.format(found, new_name, self.destination))
        copyfile(path, destination + new_name)


    def find_item(self, path, item):
        target = item['cat#']
        for image in sorted(os.listdir(path)):
            if target in image:
                self.handle_find(target, image, path + image, item)

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
        self.target_directory = Helpers.get_existing_path(Helpers.file_prompt(target_prompt), True)

        # get path for destination
        self.destination = Helpers.get_existing_path(Helpers.file_prompt(destination_prompt), True)

        # get csv path
        self.csv_path = self.target_directory = Helpers.get_existing_path(Helpers.file_prompt(csv_prompt), False)

        # parse csv
        self.raw_csv_data = pd.read_csv(self.csv_path, header=0)

        # initialize the dict
        for id,item in self.raw_csv_data.iterrows():
            self.mgcl_nums[item['cat#'].strip()] = False

        # find items
        for id,item in self.raw_csv_data.iterrows():
            self.recursive_find_item(self.target_directory + item['Genus'].strip() + '/', item)

        for mgcl_num in self.mgcl_nums:
            if not self.mgcl_nums[mgcl_num]:
                print('{} could not be located.'.format(mgcl_num))

        print()