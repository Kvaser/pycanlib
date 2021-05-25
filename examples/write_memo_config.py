"""write_memo_config.py -- Write a configuration to a memorator

This example script uses canlib.kvamemolibxml and canlib.kvmlib to load a
configuration file in .xml format, validate it, and then write it to a
connected Memorator.

It requires a configuration xml file and a connected Memorator device.

"""
import argparse

from canlib import kvamemolibxml, kvmlib


def write_config(filename, channel_number):
    # Read in the XML configuration file
    config = kvamemolibxml.load_xml_file(filename)

    # Validate the XML configuration
    errors, warnings = config.validate()

    if errors or warnings:
        raise Exception("Errors or warnings found! Check validate_memo_config example.")

    # Open the device and write the configuration
    with kvmlib.openDevice(channel_number) as memo:
        memo.write_config(config.lif)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Write a configuration to a Memorator.")
    parser.add_argument(
        'filename', default='logall.xml', nargs='?', help=("The filename of the configuration.")
    )
    parser.add_argument(
        'channel',
        type=int,
        default=0,
        nargs='?',
        help=("The channel number of the device the configuration should be written to."),
    )
    args = parser.parse_args()

    write_config(args.filename, args.channel)
