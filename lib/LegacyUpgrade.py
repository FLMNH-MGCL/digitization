import os
import re
import time
import datetime
from lib.Logger import Logger
from lib.Helpers import Helpers

# may not be necessary to have this data class
# class Occurence:
#     def __init__(self, parent_folder, file_name):
#         self._folder = parent_folder
#         self._name = file_name
    
#     @property
#     def folder(self):
#         return self._folder

#     @property
#     def name(self):
#         return self._name


class LegacyUpgrader:
    def __init__(self):
        self.parent_directory = ""
        self.edits = dict()
        self.log_file = ""
        # self.occurrences = dict()


    def get_images(self, path):
        imgs = []
        for img in sorted(os.listdir(path)):
            if os.path.isfile(path + img):
                if Helpers.valid_image(img):
                    imgs.append(img)
        return imgs

    def get_dirs(self, path):
        dirs = []
        for _dir in sorted(os.listdir(path)):
            if os.path.isdir(path + _dir):
                dirs.append(_dir)
        return dirs


    def get_digit_count(self, string):
        return sum(c.isdigit() for c in string)
    
    def get_new_name(self, old_name):
        new_name = old_name

        # remove occurrences of numbers in parentheses
        # i.e. auto naming convention for duplicates
        for par_num_str in str(re.findall(r"\(\d+\)", new_name)):
            new_name = new_name.replace(par_num_str, "").strip()

        new_name = new_name.replace("-", "_") # replace hyphens
        new_name = new_name.replace(" ", "_") # replace spaces
        new_name = new_name.replace(" ", "") # replace spaces

        if not new_name.startswith("MGCL_") and new_name.startswith("MGCL"):
            new_name = new_name.replace("MGCL", "MGCL_")
            
        # remove male / female distinction
        new_name = new_name.replace("_M", "")
        new_name = new_name.replace("_F", "")
        # new_name = new_name.replace("_C", "_CROPPED")

        # sub repeating underscores with single underscore
        new_name = re.sub("\_+", "_", new_name)

        return new_name
    
    def upgrade(self, image, working_directory):
        extension = '.' + image.split('.')[1]
        old_name = image.split('.')[0]
        new_name = self.get_new_name(old_name)

        if new_name.startswith("MGCL_"):
            img_vec = new_name.split('_')

            # check for duplicates
            if len(img_vec) > 1:
                # check for duplicate
                if os.path.exists(working_directory + new_name + extension):
                    new_name += '_DUPL'

                # check digits for error (requires exactly 7 digits)
                if self.get_digit_count(img_vec[1]) != 7:
                    print(image + ': File has digit error.')
                    new_name += '_DIGERROR'

            else:
                print(image + ': Unknown file formatting.')
                new_name += '_UNKNOWN'

        else:
            print(image + ': Unknown file formatting.')
            new_name += '_UNKNOWN'

        new_name += extension
        old_path = working_directory + image
        new_path = working_directory + new_name

        self.edits.update({old_path : new_path})

        os.rename(old_path, new_path)
        print("\nRenaming {} as {}\n".format(old_path, new_path))

    def walk(self, path):
        for subdir in self.get_dirs(path):
            self.walk(path + subdir + '/')
        
        for image in self.get_images(path):
            self.upgrade(image, path)

    def write_out(self):
        log_name = Helpers.generate_logname("LEGACY_UPGRADE",".csv", self.parent_directory)
        with open(log_name) as log_file:
            for index, (old_path,new_path) in enumerate(self.edits.items()):
                if index == 0:
                    log_file.write("old_path,new_path\n")
                else:
                    log_file.write("{},{}\n".format(old_path,new_path))
        self.log_name = log_name
    
    def delete_duplicates(self):
        for _,new_path in self.edits:
            if "_DUPL" in os.path.basename(new_path):
                try:
                    os.remove(new_path)
                except:
                    print("Could not locate {} in file system.".format(new_path))

    def undo_edits(self):
        for old_path,new_path in self.edits:
            try:
                os.rename(new_path,old_path)
            except:
                print("Could not locate {} in file system.".format(new_path))
        
        os.remove(self.parent_directory + self.log_file)

    def end_prompt(self):
        self.write_out()

        print("Please review chagnes before continuing (check log).\n")
        time.sleep(4)

        while True:
            undo = input("Do you wish to undo?\n [1]yes\n [2]no\n --> ")
            if undo == '1' or undo == 'y' or undo =='yes':
                self.undo_edits()
                return
            elif undo == '2' or undo == 'n' or undo == 'no':
                break
            else:
                print('Input error. Invalid option.')
                continue

        delete_dupl = input("Do you wish to delete any found duplicates?\n [1]yes\n [2]no\n --> ")
        if delete_dupl == '1' or delete_dupl == 'y' or delete_dupl == 'yes':
            double_check = input("Are you sure? This cannot be undone!!\n [1]yes\n [2]no\n --> ")
            if double_check == '1' or double_check == 'y' or double_check == 'yes':
                self.delete_duplicates()



    def run(self):
        print('### LEGACY UPGRADER PROGRAM ###\n')
        prompt = str(
            "\nThis program will upgrade the legacy server data to fit the new standardized filename structure. " \
            "It will first ask for you to input the directory containing the specimen images, alternatively " \
            "you may drag the folder into the terminal window on mac platforms. From there, the program will " \
            "attempt to rename all valid image files in the folder. When it is done, you will have the chance " \
            "to choose whether or not to: delete any duplicates found, undo changes or repeat program in a new " \
            "directory. 5 seconds after asking for this prompt you may begin. "
        )
        Helpers.ask_usage(prompt)

        path_prompt = "\nPlease input the path to the directory that contains the images:\n--> "
        self.parent_directory = Helpers.get_existing_path(Helpers.path_prompt(path_prompt), True)

        self.walk(self.parent_directory)
        print("All images handled...\n")
        self.end_prompt()


"""
KNOWN BUGS:
    (2) counted as dig error (should be fixed)
        fixed on personal computer, not museum. cannot repeat bug as of yet for testing.
    _2 counted as dig error (should be fixed)
"""
