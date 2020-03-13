import os
import re
import time
import datetime
from lib.Logger import Logger
from lib.Helpers import Helpers

"""
This assumes the following folder structure:
    ../families/genera/collection_dates/*specimen images here*
"""
class LegacyUpgrader:
    def __init__(self):
        self.valid_imgs = ['JPG', 'jpg', 'jpeg', 'JPEG', 'CR2', 'cr2']
        self.parent_directory = ""
        self.edits = dict()

    def is_valid(self, extension):
        if extension in self.valid_imgs:
            return True
        else: 
            return False

    def get_images(self, path):
        imgs = []
        for img in sorted(os.listdir(path)):
            if os.path.isfile(path + img):
                img_vec = img.split('.')
                if len(img_vec) > 1 and self.is_valid(img_vec[1]):
                    imgs.append(img)
        return imgs

    def FixDateFormat(self, date, path):
        return date


    def get_digit_count(self, string):
        return sum(c.isdigit() for c in string)


    def remove_duplicates(self):
        for old_name,new_name in self.edits:
            if "_DUPL" in new_name:
                try:
                    os.remove(new_name)
                except:
                    print("Could not find file.")
    
    def get_new_name(self, old_name):
        # remove male / female distinction
        new_name = old_name
        new_name = new_name.replace("-", "_") # replace hyphens
        if not new_name.startswith("MGCL_") and new_name.startswith("MGCL"):
            new_name = new_name.replace("MGCL", "MGCL_")
        new_name = new_name.replace("_M", "")
        new_name = new_name.replace("_F", "")
        # new_name = new_name.replace("_C", "_CROPPED")

        # sub repeating underscores with single underscore
        new_name = re.sub("\_+", "_", new_name)

        return new_name

    def upgrade(self):
        time.sleep(1)
        families = Helpers.get_dirs(self.parent_directory) # all the family folders
        for family in families:
            genera = Helpers.get_dirs(self.parent_directory + family + '/') # all the genus folders
            for genus in genera:
                collection = Helpers.get_dirs(self.parent_directory + family + '/' + genus + '/') # all the date folders
                for date in collection:
                    working_directory = self.parent_directory + family + '/' + genus + '/' + date + '/'
                    specimens = self.get_images(working_directory)
                    visited = []
                    for specimen in specimens:
                        extension = '.' + specimen.split('.')[1]
                        old_name = specimen.split('.')[0]
                        new_name = self.get_new_name(old_name)

                        if new_name.startswith("MGCL_"):
                            img_vec = new_name.split('_')

                            # check for duplicates
                            if len(img_vec) > 1:
                                # check for duplicate
                                if new_name in visited:
                                    new_name += '_DUPL'
                                else:
                                    visited.append(new_name)

                                # check digits for error (requires exactly 7 digits)
                                if self.get_digit_count(img_vec[1]) != 7:
                                    print(specimen + ': File has digit error.')
                                    new_name += '_DIGERROR'

                            else:
                                print(specimen + ': Unknown file formatting.')
                                new_name += '_UNKNOWN'

                        else:
                            print(specimen + ': Unknown file formatting.')
                            new_name += '_UNKNOWN'

                        new_name += extension
                        old_path = working_directory + specimen
                        new_path = working_directory + new_name

                        self.edits.update({old_path : new_path})

                        os.rename(old_path, new_path)
                        print("\nRenaming {} as {}\n".format(old_path, new_path))

        print("All images handled. Please hold...\n")

    def run(self):
        print('### LEGACY UPGRADER PROGRAM ###\n')
        print('NOTE: logging is temporarily down...\n')
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

        self.upgrade()


# def Wait(path):
#     time.sleep(5)

#     wait = True
#     print("Program completed... Please review changes.")

#     delete_dupl = input("Do you wish to delete any found duplicates?\n [1]yes\n [2]no\n --> ")
#     if delete_dupl == '1' or delete_dupl == 'y' or delete_dupl == 'yes':
#         double_check = input("Are you sure? This cannot be undone!!\n [1]yes\n [2]no\n --> ")
#         if double_check == '1' or double_check == 'y' or double_check == 'yes':
#             # DeleteDupl()
#             print("Deleting will be functional after proper testing...")

#     while wait == True:
#         undo = input("Do you wish to undo?\n [1]yes\n [2]no\n --> ")
#         if undo == '1' or undo == 'y' or undo =='yes':
#             print(Undo())
#             wait = False
#         elif undo == '2' or undo == 'n' or undo == 'no':
#             wait = False
#             Log(path)
#         else:
#             print('Input error. Invalid option.')
#             continue

#     repeat = input ("Do you want to repeat program in a new parent directory?\n [1]yes\n [2]no\n --> ")
#     if repeat == '1' or repeat == 'y' or repeat == 'yes':
#         old_new_paths.clear()
#         duplicates.clear()
#         unknowns.clear()
#         AskUsage()
#         Upgrade(DirPrompt())
#     else:
#         print("Exiting...")
#         time.sleep(2)


"""
KNOWN BUGS:
    (2) counted as dig error (should be fixed)
        fixed on personal computer, not museum. cannot repeat bug as of yet for testing.
    _2 counted as dig error (should be fixed)
    not duplicates if diff orientations ? (fixed)
    fix duplicate calc, eg Dorsal Dorsal Ventral not counted (fixed)
    MGCL- "MGCL hyphen" #Replace w/ underscores
    MGCL# (no separation)   #Replace MGCL w/ MGCL_
"""
