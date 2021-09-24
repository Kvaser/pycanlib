"""convert_kme_asc.py -- Convert a .kme50 logfile into plain ASCII

This example script uses canlib.kvlclib to convert a logfile from .kme50 format
into plain ASCII.

"""
import argparse
from pathlib import Path

from canlib import kvlclib


def try_set_propery(cnv, property, value=None):
    # Check if the format supports the given property
    if cnv.format.isPropertySupported(property):
        # If a value is specified, set the property to this value
        if value is not None:
            cnv.setProperty(property, value)

        # Get the property's default value
        default = cnv.format.getPropertyDefault(property)
        print(f'  {property} is supported (Default: {default})')

        # Get the property's current value
        value = cnv.getProperty(property)
        print(f'    Current value: {value}')
    else:
        print(f'  {property} is not supported')


def convert_events(cnv):
    # Get estimated number of remaining events in the input file. This
    # can be useful for displaying progress during conversion.
    total = cnv.eventCount()
    print(f"Converting about {total} events...")
    while True:
        try:
            # Convert events from input file one by one until EOF
            # is reached
            cnv.convertEvent()
            if cnv.isOutputFilenameNew():
                print(f"New output filename: '{cnv.getOutputFilename()}'")
                print(f"About {cnv.eventCount()} events left...")
        except kvlclib.KvlcEndOfFile:
            if cnv.isOverrunActive():
                print("NOTE! The extracted data contained overrun.")
                cnv.resetOverrunActive()
            if cnv.isDataTruncated():
                print("NOTE! The extracted data was truncated.")
                cnv.resetStatusTruncated()
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert a .kme50 logfile into plain ASCII.")
    parser.add_argument(
        'filename', metavar='LOGFILE.KME50', help=("The filename of the .kme50 logfile.")
    )
    args = parser.parse_args()
    in_file = Path(args.filename)

    # set up formats
    out_fmt = kvlclib.WriterFormat(kvlclib.FileFormat.PLAIN_ASC)
    in_fmt = kvlclib.ReaderFormat(kvlclib.FileFormat.KME50)

    # set resulting output file name taking advantage of the extension
    # defined in the format.
    out_file = in_file.with_suffix('.' + out_fmt.extension)
    print(f"Output filename is '{out_file}'")

    # create converter
    cnv = kvlclib.Converter(out_file, out_fmt)

    # Set input file and format
    cnv.setInputFile(in_file, kvlclib.FileFormat.KME50)

    # split output files into max 100 MB files
    # The name of the resulting files will now end in '-partX.txt',
    # thus the first file will be named logfile-part0.txt, assuming we use
    # logfile.kme50 as input file name.
    try_set_propery(cnv, kvlclib.Property.SIZE_LIMIT, 100)

    # allow output file to overwrite existing files
    try_set_propery(cnv, kvlclib.Property.OVERWRITE, 1)

    # we are only interested in the first channel
    cnv.setProperty(kvlclib.Property.CHANNEL_MASK, 1)

    # add nice header to the output file
    try_set_propery(cnv, kvlclib.Property.WRITE_HEADER, 1)

    # we are converting CAN traffic with max 8 bytes, so we can minimize
    # the width of the data output to 8 bytes
    try_set_propery(cnv, kvlclib.Property.LIMIT_DATA_BYTES, 8)

    convert_events(cnv)

    # force flush result to disk
    cnv.flush()
