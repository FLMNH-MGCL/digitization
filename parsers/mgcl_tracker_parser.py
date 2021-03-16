import argparse
import textwrap

# this is not a great naming scheme
def mgcl_tracker_parser(sub_parsers, parent):
    description = "Track the used MGCL numbers in the filesystem"

    mgcl_tracker_parser = None

    if sub_parsers is None and parent is None:
        mgcl_tracker_parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(
                """\
                Example Runs:
                python3 ./mgcl_tracker.py --start_dir /fake/path --range 1234567 2000000
                python3 ./mgcl_tracker.py --start_dir /fake/path --range 1234567 2000000 --exts png jpg
                python3 ./mgcl_tracker.py --start_dir /fake/path --file /fake/path/file.csv
                """
            ),
        )
    else:
        mgcl_tracker_parser = sub_parsers.add_parser(
            name="mgcl_tracker",
            add_help=False,
            help=description,
        )

    mgcl_tracker_parser.add_argument(
        "-d",
        "--start_dir",
        required=True,
        type=str,
        help="path to the starting directory",
    )

    mgcl_tracker_parser.add_argument(
        "-e",
        "--exts",
        required=False,
        nargs="+",
        default=["png", "jpg", "jpeg"],
        help="The upper bound MGCL number to include in count (default is png jpg jpeg)",
    )

    # this group will be for EITHER specifying a range of MGCL numbers to search for
    # OR to use a CSV/XLSX of MGCL nums, which is why I made it a mutually exclusive group
    group = mgcl_tracker_parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-r",
        "--range",
        nargs=2,
        metavar=("LOWER", "UPPER"),
        help="The lower and upper bound MGCL numbers, from LOWER to UPPER (inclusive)",
    )

    group.add_argument("-f", "--file", help="A CSV of MGCL Numbers to search for")

    return mgcl_tracker_parser