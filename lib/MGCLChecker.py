"""
  MGCL DUPLICATE CHECK: -> DIGITIZATION.py
    OVERVIEW:
      dictionary of file names split to only include MGCL
      ignore downscaled
"""

import os
from pathlib import Path
from lib.Helpers import Helpers
import re

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

  def extract_family_genus(self, filepath):
    pattern = r"[a-z]*dae[\\/][a-z]*"
    family_genus = re.search(pattern, filepath, re.IGNORECASE)

    if not family_genus:
      # print("Cannot determine family or genus from path to file: {}".format(filepath))
      return None

    family_genus = family_genus.group()
    print(family_genus)

    if family_genus == "":
      return None
    
    family_genus.replace("\\", "/")
    family_genus_vec = family_genus.split("/")

    if len(family_genus_vec) < 2:
      # print("Cannot determine family or genus from path to file: {}".format(filepath))
      return None
    

    return family_genus_vec


  def calculate_priority(self, target, occurrence_list):
    # if they have same genus and family they are low priority, likely just duplicated numbers
    # if they have same family but different genus, high priority

    target_family_genus = self.extract_family_genus(target)

    if not target_family_genus:
      print("Cannot determine family or genus from path to file: {}".format(target))
      return "cannot determine"

    family = target_family_genus[0]
    genus = target_family_genus[1]

    priority = ""
    had_indeterminate = False

    for occurrence in occurrence_list:
      # get genus & family of occurrence
      family_genus = self.extract_family_genus(occurrence[0])

      if not family_genus:
        print("Cannot determine family or genus from path to file: {}".format(target))
        had_indeterminate = True
        continue
        
      
      o_family = family_genus[0]
      o_genus = family_genus[1]

      if o_genus == genus and o_family == family and priority != "high priority":
        priority = "low priority"
        continue

      if o_family == family and o_genus != genus:
        priority = "high priority"

      if o_family != family:
        priority = "high priority"

    
      
    if had_indeterminate and priority == "":
      return "cannot determine"
    
    elif priority == "":
      return "low priority"

    return priority


  def write_out(self):
    """
      will write out data to csv. valid and singularly occurring images will not 
      be logged. duplicates and invalids will be logged to csv. csv format 
      will be: filepath,isDup,isValid
    """
    csv_name = Helpers.generate_logname("MGCL_CHECKER", ".csv", self.target_directory)
    print("Writing invalid or duplicate values to: {}/{}\n".format(self.target_directory,csv_name))
    dest_file = open(r"{}/{}".format(self.target_directory, csv_name),"w+")
    dest_file.write(",path to file,has duplicate,is valid\n")

    for key in self.scanned:
      occurrence_list = self.scanned[key]
      is_dup = False
      priority = ""

      if len(occurrence_list) > 1:
        is_dup = True

      for item in occurrence_list:  
        # print("path to file: {}\nhas duplicate: {}\nis valid: {}\n".format(item[0], is_dup, item[1]))
        # only write files that are dups or invalid
        if is_dup or not item[1]:
          priority = self.calculate_priority(item[0], occurrence_list)
          dest_file.write("{},{},{},{}\n".format(priority, item[0], is_dup, item[1]))
      
    dest_file.close()

  def verfiy_files(self, files):
    """
      iterate through all the files, check if they exist in the 'self.scanned' dictionary.
      if they do, add to duplicates. Add unhandled edge cases to 'self.edge_cases'
    """
    print("\nFiles collected... Analyzing...\n")
    for filepath in files:
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

    print("\nProgram completed.\n")
    self.reset()


