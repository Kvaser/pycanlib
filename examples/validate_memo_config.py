"""validate_memo_config.py -- validate a Memorator configuration

This script uses canlib.kvamemolibxml to load and validate a Memorator
configuration in an xml file, and then prints any errors and warnings.

It requires a Memorator configuration in xml format.

"""
import argparse

from canlib import kvamemolibxml


def validate(filename):
    # Read in the XML configuration file
    config = kvamemolibxml.load_xml_file(filename)

    # Validate the XML configuration
    errors, warnings = config.validate()

    # Print errors and warnings
    for error in errors:
        print(error)
    for warning in warnings:
        print(warning)

    if errors or warnings:
        raise Exception("Please fix validation errors/warnings.")
    else:
        print("No errors found!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate a Memorator configuration.")
    parser.add_argument(
        'filename', default='logall.xml', nargs='?', help=("The filename of the configuration.")
    )
    args = parser.parse_args()

    validate(args.filename)
