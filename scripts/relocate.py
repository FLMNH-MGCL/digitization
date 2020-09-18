from enum import Enum, unique
import sys
import os
import pandas as pd
import pathlib
import shutil
import argparse
import textwrap
from datetime import datetime

def error_message(message, exit=True):
  print("relocate.py: error:", message)

  if exit:
    sys.exit(1) 

@unique
class ConfigTypes(Enum):
  DEFAULT = "DEFAULT"
  MGCLCHECKER = "MGCLCHECKER"

  def __eq__(self, rhs):
    return self.name == rhs

class Relocator:
  def __init__(self, config=ConfigTypes.DEFAULT, log_location="", destination=""):
    self.config = config
    self.log_location = log_location
    self.destination = destination
    self.failures = []

  @staticmethod
  def check_valid_construction(log, destination):
    if not os.path.exists(log) and not os.path.isfile(log) and pathlib.Path(log).suffix != ".csv":
      error_message("{} either does not exist or is the wrong file type".format(log))

    if not os.path.exists(destination) and not os.path.isdir(destination):
      error_message("{} either does not exist or is not a directory".format(destination))

  def mgclchecker(self):
    raw_data = pd.read_csv(self.log_location)

    for _, row in raw_data.iterrows():
      path = ""

      try:
        path = str(row['path'])
      except:
        error_message("csv file improperly formatted for MGCLChecker relocation. attempted access to 'path' header, returned None")
      
      filename = os.path.basename(path)
      try:
        new_location = os.path.abspath(os.path.join(self.destination, filename))
        old_location = os.path.abspath(path)
        print("attempting copy of {} to {}".format(old_location, new_location))

        shutil.copyfile(old_location, new_location)
      except Exception as exception:
        print(exception)
        error_message("{}... failed to copy {}... skipping".format(exception, old_location), False)
        self.failures.append(old_location)
      
      print()

  def run(self):
    if self.config == ConfigTypes.MGCLCHECKER:
      self.mgclchecker()


def cli():
  my_parser = argparse.ArgumentParser(description="Relocate troublesome images based on the log output of other scripts", 
  formatter_class=argparse.RawDescriptionHelpFormatter,
  epilog=textwrap.dedent('''\
          Config Types:
            MGCLCHECKER

          Example Runs:
            python3 ./relocate.py --config MGCLCHECKER --log /path/to/log.csv --destination /new/parent/directory
         '''))

  my_parser.add_argument('-c', '--config', required=True, type=str, help="the log type (based on script that generated it)")
  my_parser.add_argument('-l', '--log', required=True, type=str, help="path to the log file")
  my_parser.add_argument('-d', '--destination', required=True, type=str, help="path to the new directory")

  args = my_parser.parse_args()

  try:
    config = ConfigTypes[args.config]
  except:
    error_message("{} is not a valid config type. run '--help' to see all accepted configurations")

  log = args.log
  destination = args.destination

  Relocator.check_valid_construction(log, destination)

  relocator = Relocator(config, os.path.abspath(log), os.path.abspath(destination))
  print("Program starting...\n")
  relocator.run()
  print("\nAll computations completed...")


if __name__ == "__main__":
  cli()