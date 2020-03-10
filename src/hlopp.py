import pandas as pd
from pathlib import Path
import os
import math
from Logger import Logger
from Helpers import Helpers


# excel_path = input().strip()

# data = pd.read_csv(excel_path, header=0)

# for i in data.itertuples():
#     print(i)
class HloppReader:
    def __init__(self):
        self.csv_path = ""
        self.target_directory = ""
        self.hlopp_to_mgcl = dict()
        self.error_log = []
        self.edits = dict()
        self.logger = None

    def init_logger(self):
        csv_file = self.csv_path
        csv_file = self.csv_path.split('/')
        csv_file = csv_file[len(csv_file) - 1]
        raw_path = self.csv_path[:(-1 * len(csv_file))]
        self.logger = Logger(raw_path, 'HLOPP_CONVERT')
    
    def parse_csv(self):
        print('\nParsing CSV file...\n')
        raw_data = pd.read_csv(self.csv_path, header=0)
        pairs = dict()

        for id,row in raw_data.iterrows():
            pairs.update({row['HLOPP#'] : row['MGCL_barcode']})

        self.hlopp_to_mgcl = pairs
    
    def isolate_filename(self, file):
        file = file.replace('\\', '/')
        path_vector = file.split('/')
        return path_vector[len(path_vector) - 1]

    def rename_occurrences(self, occurrences):
        for file in occurrences:
            filename = self.isolate_filename(file)
            raw_filename = filename.split('.')[0]

            ext = ''
            try:
                ext = '.' + filename.split('.')[1]
            except:
                ext = ''
            
            mgcl_rename = self.hlopp_to_mgcl.get(raw_filename)
            if mgcl_rename is None:
                # log error
                continue
            else:
                # rename
                new_path = file[:(-1 * len(filename))]
                new_path += mgcl_rename + ext
                print('Renaming {} as {}'.format(file, new_path))
                # os.rename(file, new_path)
                self.edits.update({file : new_path})

    def init_convert(self):
        print('Initializing the conversions...\n')
        files = list(dict((str(f), f.stat().st_size) for f in Path(self.target_directory).glob('**/*') if f.is_file()).keys())

        for hlopp,mgcl in self.hlopp_to_mgcl.items():
            # print(mgcl)
            if not type(mgcl) is str or not type(hlopp) is str:
                continue
            if not 'MGCL' in mgcl:
                continue

            occurrence_indices = [index for index, file in enumerate(files) if hlopp in file]
            occurrences = []

            for index in occurrence_indices:
                occurrences.append(files[index])

            self.rename_occurrences(occurrences)


    def wait(self):
        print('\nConversion completed.')
        if len(self.error_log) > 0:
            print('Errors detected: {}\n'.format(len(self.error_log)))
            print('Would you like to review errors before exiting? (Note, they will be logged regardless)')

            review = input('[1] yes\n[2] no\n -->')
            if review in ['1', 'y', 'yes']:
                print(self.error_log)
        else:
            print('No errors detected.')
        
        print('\nWould you like to undo the changes made? (This will override the automatic error log)')
        undo = input('[1] yes\n[2] no\n--> ')

        if undo in ['1', 'y', 'yes']:
            self.undo()
        else:
            print('\nChanges remain. Exiting. See log for changes / errors')
            self.logger.set_log_content(self.edits)
            self.logger.set_error_content(self.error_log)
            self.logger.write_out()

    def undo(self):
        for old_path,new_path in self.edits.items():
            os.rename(new_path, old_path)
    
    def run(self):
        csv_prompt = '\nPlease input the path to the csv file that contains the HLOPP to convert to MGCL standard: \n --> '
        path_prompt = '\nPlease input the path to the directory that contains the files: \n --> '
        self.csv_path = Helpers.get_existing_path(Helpers.file_prompt(csv_prompt), False)
        self.target_directory = Helpers.get_existing_path(Helpers.path_prompt(path_prompt), True)
        self.init_logger()
        self.parse_csv()
        self.init_convert()
        self.wait()


def main():
    program = HloppReader()
    program.run()

if __name__ == "__main__":
    main()
