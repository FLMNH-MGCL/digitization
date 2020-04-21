import sys
import os
import time
import imageio
import rawpy
from lib.Helpers import Helpers

class Converter:
    def __init__(self):
        self.target_directory = ""

    def isJPG(self, f):
        parsedName = f.split(".")

        if len(parsedName) < 2: 
            return False
        elif parsedName[1].lower() in ["jpg", "jpeg"]:
            return True
        else: return False
    
    def isCR2(self, f):
        parsedName = f.split(".")

        if len(parsedName) < 2: 
            return False
        elif parsedName[1].lower() == "cr2":
            return True
        else: return False

    def getImgs(self, path):
        jpgs = []
        cr2s= []
        for f in sorted(os.listdir(path)):
            if os.path.isfile(path + f):
                if self.isJPG(f):
                    jpgs.append(f)
                elif self.isCR2(f):
                    cr2s.append(f)
                else: continue

        return (jpgs, cr2s)

    def alreadyConverted(self, path, cr2):
        permutations = [".jpg", ".JPG", ".jpeg", ".JPEG"]
        jpg = path + cr2.split(".")[0]
        
        for ext in permutations:
            if os.path.exists(jpg + ext):
                return True
        
        return False

    def standard_run(self, path):
        print('\nCurrently working in {}'.format(path))
        allImages = self.getImgs(path)
        jpgs = allImages[0]
        cr2s = allImages[1]

        if len(jpgs) == len(cr2s):
            print("Folder already handled...")
            return
        
        for cr2 in cr2s:
            if not self.alreadyConverted(path, cr2):
                print("Converting {} to JPG format...".format(cr2))
                with rawpy.imread(path + cr2) as raw:
                    rgb = raw.postprocess(user_wb=[1, 0.5, 1, 0])
                    name = cr2.split('.')[0] + '.jpg'
                    imageio.imsave(path + name, rgb)

    def recursive_run(self, path):
        for subdir in Helpers.get_dirs(path):
            self.recursive_run(path + subdir + "/")
        self.standard_run(path)

    def run(self):
        print("### CONVERT CR2 -> JPG PROGRAM ###\n")
        help_prompt = str(
            "Help to come soon..."
        )
        Helpers.ask_usage(help_prompt)
        
        path_prompt = "\nPlease input the path to the directory that contains the images:\n--> "
        self.target_directory = Helpers.get_existing_path(Helpers.path_prompt(path_prompt), True)

        recurse_prompt = str("\nChoose 1 of the following: \n [1]Standard (All files in this directory level) \n [2]Recursive " \
            "(All files in this directory level and every level below) \n\n--> ")
        recurse = Helpers.rescurse_prompt(recurse_prompt)

        if recurse:
            self.recursive_run(self.target_directory)
        else:
            self.standard_run(self.target_directory)
        
        print("\nProgram complete.\n")