import pandas as pd
from lib.Helpers import Helpers

class UniqueExcel:
    def __init__(self):
        self.csv_path = ""
        self.destination = ""
        # self.error_log = []
        self.raw_csv_data = None
        self.unique_values = dict()

    def write_out(self):
        print("Writing values to: {}/UNIQUE_VALUES.txt".format(self.destination))
        dest_file = open(r"{}/UNIQUE_VALUES.txt".format(self.destination),"w+")
        
        for col in self.unique_values:
            dest_file.write("{} : [ ".format(col))
            for item in self.unique_values[col]:
                dest_file.write("{}, ".format(item))
            dest_file.write(" ]\n\n")
        
        dest_file.close()
  
    def run(self):
        csv_prompt = "\nPlease enter the path to the CSV file: \n--> "
        destination_prompt = "\nPlease input the path you would like the unique value document to go: \n--> "
        
        print("### UNIQUE VALUE FINDER PROGRAM ###\n")

        help_prompt = str(
            "\nThis program will analyze a CSV file and write out a text (.txt) file containing each column and that "\
            "column's unique values as a list. For example, let's say your CSV looked something like this:\n\n"\
            "puppy_breed, puppy_name, cuteness_level\ngolden,henry,100M\ngolden,shay,100M\n\nthe text document would "\
            "look something like: \n\npuppy_breed : [golden]\npuppy_name : [henry,shay]\ncuteness_level : [100M]"
        )
        Helpers.ask_usage(help_prompt)

        # get csv path
        self.csv_path = self.target_directory = Helpers.get_existing_path(Helpers.file_prompt(csv_prompt), False)

        # get path for destination
        self.destination = Helpers.get_existing_path(Helpers.file_prompt(destination_prompt), True)

        # parse csv
        print("\nParsing CSV...\n")
        self.raw_csv_data = pd.read_csv(self.csv_path, header=0, encoding = "ISO-8859-1", low_memory=False)

        print("Finding unique values...\n")
        for col in self.raw_csv_data:
            # print(col)
            # print(self.raw_csv_data[col].unique())
            self.unique_values[col] = self.raw_csv_data[col].unique()

        # print(self.unique_values)

        self.write_out()

# testing:
# file : C:\Users\aaron\Documents\museum\FLMNH\testing\test.csv
# dest : C:\Users\aaron\Documents\museum