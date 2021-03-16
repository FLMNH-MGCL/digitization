import argparse
from parsers import mgcl_tracker_parser

############### PROOF OF CONCEPT ###############
# i.e. not ready for usage
#
# the idea here is to have one parent script with all
# the others as subcommands.
#
# e.g. python3 dig.py --help --> prints dig.py help
# e.g. python3 dig.py mgcl_tracker --help -->
#   prints mgcl_tracker help
###############################################

main_parser = argparse.ArgumentParser(
    description="Select and run a digitization script", add_help=True
)

sub_parsers = main_parser.add_subparsers(title="Available Scripts")
sub_parsers.required = True

# i need to figure out a better module/function naming scheme for this
mgcl_tracker = mgcl_tracker_parser.mgcl_tracker_parser(sub_parsers, main_parser)

args = main_parser.parse_args()
