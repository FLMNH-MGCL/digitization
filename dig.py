# import argparse

# from parsers import mgcl_tracker_parser
# from scripts import (
#     # dynaiello,
#     # gene_copy,
#     mgcl_tracker,
#     # protein_combine,
#     # relocate,
#     # suspect_numbers,
#     # unique_values,
#     # wrangler,
# )

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


# def main():
#     main_parser = argparse.ArgumentParser(
#         description="Select and run a digitization script", add_help=True
#     )

#     sub_parsers = main_parser.add_subparsers(dest="scripts")
#     mgcl_tracker_parser.mgcl_tracker_parser(sub_parsers)

#     args = main_parser.parse_args()

#     if args.scripts == "mgcl_tracker":
#         mgcl_tracker.run(args)


# if __name__ == "__main__":
#     main()


# parsers/mgcl_tracker_parser.py
#
# import argparse
# import textwrap

# # this is not a great naming scheme
# def mgcl_tracker_parser(sub_parsers):
#     description = "Track the used MGCL numbers in the filesystem"

#     mgcl_tracker_parser = None

#     if sub_parsers is None:
#         mgcl_tracker_parser = argparse.ArgumentParser(
#             description=description,
#             formatter_class=argparse.RawDescriptionHelpFormatter,
#             epilog=textwrap.dedent(
#                 """\
#                 Example Runs:
#                 python3 ./mgcl_tracker.py --start_dir /fake/path --range 1234567 2000000
#                 python3 ./mgcl_tracker.py --start_dir /fake/path --range 1234567 2000000 --exts png jpg
#                 python3 ./mgcl_tracker.py --start_dir /fake/path --file /fake/path/file.csv
#                 """
#             ),
#         )
#     else:
#         mgcl_tracker_parser = sub_parsers.add_parser(
#             name="mgcl_tracker",
#             add_help=False,
#             help=description,
#         )

#     mgcl_tracker_parser.add_argument(
#         "-d",
#         "--start_dir",
#         required=True,
#         type=str,
#         help="path to the starting directory",
#     )

#     mgcl_tracker_parser.add_argument(
#         "-e",
#         "--exts",
#         required=False,
#         nargs="+",
#         default=["png", "jpg", "jpeg"],
#         help="The upper bound MGCL number to include in count (default is png jpg jpeg)",
#     )

#     # this group will be for EITHER specifying a range of MGCL numbers to search for
#     # OR to use a CSV/XLSX of MGCL nums, which is why I made it a mutually exclusive group
#     group = mgcl_tracker_parser.add_mutually_exclusive_group(required=True)

#     group.add_argument(
#         "-r",
#         "--range",
#         nargs=2,
#         metavar=("LOWER", "UPPER"),
#         help="The lower and upper bound MGCL numbers, from LOWER to UPPER (inclusive)",
#     )

#     group.add_argument("-f", "--file", help="A CSV of MGCL Numbers to search for")

#     return mgcl_tracker_parser