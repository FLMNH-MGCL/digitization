import argparse
from parsers import mgcl_tracker_parser
from scripts import (
    # dynaiello,
    # gene_copy,
    mgcl_tracker,
    # protein_combine,
    # relocate,
    # suspect_numbers,
    # unique_values,
    # wrangler,
)

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


def main():
    main_parser = argparse.ArgumentParser(
        description="Select and run a digitization script", add_help=True
    )

    sub_parsers = main_parser.add_subparsers(dest="scripts")
    mgcl_tracker_parser.mgcl_tracker_parser(sub_parsers, main_parser)

    args = main_parser.parse_args()

    if args.scripts == "mgcl_tracker":
        mgcl_tracker.run(args)


if __name__ == "__main__":
    main()
