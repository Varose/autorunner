""" Convert HAR (HTTP Archive) to YAML/JSON testcase for AutoRunner.

Usage:
    # convert to JSON format testcase
    $ hrun har2case demo.har

    # convert to YAML format testcase
    $ hrun har2case demo.har -2y

"""

from autorunner.ext.har2case.core import HarParser
from autorunner.utils import ga_client


def init_har2case_parser(subparsers):
    """ HAR converter: parse command line options and run commands.
    """
    parser = subparsers.add_parser(
        "har2case",
        help="Convert HAR(HTTP Archive) to YAML/JSON testcases for AutoRunner.",
    )
    parser.add_argument("har_source_file", nargs="?", help="Specify HAR source file")
    parser.add_argument(
        "-2y",
        "--to-yml",
        "--to-yaml",
        dest="to_yaml",
        action="store_true",
        help="Convert to YAML format, if not specified, convert to pytest format by default.",
    )
    parser.add_argument(
        "-2j",
        "--to-json",
        dest="to_json",
        action="store_true",
        help="Convert to JSON format, if not specified, convert to pytest format by default.",
    )
    parser.add_argument(
        "--filter",
        help="Specify filter keyword, only url include filter string will be converted.",
    )
    parser.add_argument(
        "--exclude",
        help="Specify exclude keyword, url that includes exclude string will be ignored, "
        "multiple keywords can be joined with '|'",
    )
    parser.add_argument(
        "--profile",
        dest="profile",
        help="Specify yaml file to overwrite headers and cookies in HAR.",
    )

    return parser


def main_har2case(args):
    har_source_file = args.har_source_file

    if args.to_yaml:
        output_file_type = "YAML"
    elif args.to_json:
        output_file_type = "JSON"
    else:
        output_file_type = "pytest"

    ga_client.track_event("ConvertTests", f"har2case {output_file_type}")
    HarParser(har_source_file, args.filter, args.exclude, args.profile).gen_testcase(output_file_type)

    return 0
