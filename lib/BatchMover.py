import os
import pandas as pd
import shutil
from lib.Helpers import Helpers

class BatchMover:
    def __init__(self):
        self.csv_path = ""
        self.error_log = []
        self.raw_csv_data = None
    
    def reset(self):
        self.csv_path = ""
        self.destination = ""
        self.starting_folder = ""
        self.error_log = []
        self.raw_csv_data = None

    def write_out(self):
        if len(self.error_log) == 0:
            return
        
        filepath = os.path.dirname(self.csv_path) + "/"
        filename = Helpers.generate_logname("BATCH_MOVER_ERRORS",".txt", filepath)
        filepath = filepath + filename
        print("\nErrors detected, writing to ", filepath)
        with open(filepath, "w") as f:
            for line in self.error_log:
                f.write(line + "\n")
 

    def attempt_relocate(self, currentPath, newPath):
        """
            Attempts to move the file from currentPath to newPath.
        """
        # check that current path exists
        current_exists = os.path.exists(currentPath) and os.path.isfile(currentPath)

        if current_exists:
            try:
                shutil.move(currentPath, newPath)
                return True,"Successfully moved {} to {}".format(currentPath, newPath)
            except:
                return False,"Error. Could not move {} to {}".format(currentPath, newPath)
        else:
            return False,"{} does not exist in filesystem or is not a file.".format(currentPath)

    def run(self):
        csv_prompt = "\nPlease enter the path to the properly formatted CSV file: \n--> "

        print("### BATCH MOVER PROGRAM ###")

        # get csv path
        self.csv_path = self.target_directory = Helpers.get_existing_path(Helpers.file_prompt(csv_prompt), False)
        print()

        # parse csv
        self.raw_csv_data = pd.read_csv(self.csv_path, header=0)

        for id,item in self.raw_csv_data.iterrows():
            currentPath = item["currentPath"]
            newPath = item["newPath"]
            success = self.attempt_relocate(currentPath, newPath)

            if success[0]:
                print(success[1])
            else:
                self.error_log.append(success[1])

        self.write_out()
        print("\nProgram completed.\n")
        self.reset()