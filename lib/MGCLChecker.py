"""
  MGCL DUPLICATE CHECK: -> DIGITIZATION.py
    OVERVIEW:
      dictionary of file names split to only include MGCL
      ignore downscaled
"""

import os
from pathlib import Path
from lib.Helpers import Helpers

class MGCLChecker:
  def __init__(self):
    self.target_directory = ""

    # { filename, [(path, valid)] }
    self.scanned = dict()

    # path
    self.duplicates = []

    # contains invalids or other
    self.edge_cases = []

    # self.error_log = []

  def reset(self):
    self.target_directory = ""
    self.scanned = dict()
    self.duplicates = []
    self.edge_cases = []


  def collect_files(self):
    return list(dict((str(f), f.stat().st_size) for f in Path(self.target_directory).glob('**/*') if (f.is_file() and "duplicate" not in str(f) and Helpers.valid_image(str(f)))).keys())


  def is_img(self, filename):
    sanity_check = filename.split(".")

    if len(sanity_check) < 2:
      print("{} failed sanity check (no file extension found)".format(filename))
      return False

    ext = sanity_check[1]
    if not Helpers.valid_image("." + ext):
      print("{} is not a valid file type for this program".format(filename))
      return False

    return True


  def is_valid(self, filename):
    name_vec = filename.split("_")
      
    # missing _
    if len(name_vec) < 2:
      print("{} missing underscore".format(filename))
      return False

    if name_vec[0] != "MGCL":
      print("{} does not start with MGCL".format(filename))
      return False

    mgcl_num = name_vec[1].split(".")[0]
    if len(mgcl_num) < 6:
      print("{}: {} is too small of a number".format(filename, mgcl_num))
      return False

    if not Helpers.is_int(mgcl_num):
      print("{}: detected non-integer value for number in filename".format(filename))
      return False

    return True


  def write_out(self):
    # csv => filepath,isDup,isValid
    """
      will write out data to csv. valid and singularly occurring images will not 
      be logged. duplicates and invalids will be logged to csv. csv format 
      will be: filepath,isDup,isValid
    """
    csv_name = Helpers.generate_logname("MGCL_CHECKER", ".csv", self.target_directory)
    print("Writing invalid or duplicate values to: {}/{}\n".format(self.target_directory,csv_name))
    dest_file = open(r"{}/{}".format(self.target_directory, csv_name),"w+")
    dest_file.write("path to file,has duplicate,is valid\n")

    for key in self.scanned:
      ocurrence_list = self.scanned[key]
      is_dup = False

      if len(ocurrence_list) > 1:
        is_dup = True
      for item in ocurrence_list:
        print("path to file: {}\nhas duplicate: {}\nis valid: {}\n".format(item[0], is_dup, item[1]))
        # only write files that are dups or invalid
        if is_dup or not item[1]:
          dest_file.write("{},{},{}\n".format(item[0], is_dup, item[1]))
      
    dest_file.close()

  def verfiy_files(self, files):
    """
      iterate through all the files, check if they exist in the 'self.scanned' dictionary.
      if they do, add to duplicates. Add unhandled edge cases to 'self.edge_cases'
    """
    # print(files)
    # return
    print("\nFiles collected... Analyzing...\n")
    for filepath in files:
      # print(filepath)
      filename = os.path.basename(filepath)
      valid = True

      if not self.is_img(filename):
        continue

      if not self.is_valid(filename):
        valid = False
        # self.edge_cases.append(filepath)

      if filename in self.scanned:
        self.scanned[filename].append((filepath, valid))

      else:
        self.scanned[filename] = []
        self.scanned[filename].append((filepath, valid))
      
    self.write_out()

  
  def run(self):
    print("### MGCL CHECKER PROGRAM ###\n")
    destination_prompt = "\nPlease input the path you would like to start the check: \n--> "
    help_prompt = str(
      "\nThis program will search through a filesystem at a user inputted starting point, "
      "and attempt to find any misformatted / duplicated filenames."
    )
    Helpers.ask_usage(help_prompt)

    # get starting path
    self.target_directory = Helpers.get_existing_path(Helpers.file_prompt(destination_prompt), True)

    print("\nCollecting files...")
    self.verfiy_files(self.collect_files())
    # print(files)

    print("\nProgram completed.\n")
    self.reset()


