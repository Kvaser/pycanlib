"""dbmonitorfd.py -- Read CAN FD messages using a database

This script will use canlib.canlib and canlib.kvadblib to monitor a CAN FD
channel, and look up all messages received in a database before printing them.

It requires a CANlib channel with a connected device capable of receiving CAN FD
messages, some source of CAN messages, and the same database that the source is
using to generate the messages.

The script also reuses the monitor_channel function defined in dbmonitor.py

The source of the messages may be e.g. the pingerfd.py example script.

"""
import argparse

from canlib import canlib, kvadblib

import dbmonitor

# Create a dictionary of predefined CAN FD bitrates, using the name after
# "BITRATE_" as key. E.g. "500K_80P".
fd_bitrates = {x.name.replace("BITRATE_", ""): x for x in canlib.BitrateFD}


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Listen on a CAN channel and print all signals received, as specified by a database."
    )
    parser.add_argument(
        'channel', type=int, default=1, nargs='?', help=("The channel to listen on.")
    )
    parser.add_argument(
        '--db',
        default="engine_example.dbc",
        help=("The database file to look up messages and signals in."),
    )
    parser.add_argument(
        '--fdbitrate', '-f', default=['500k_80p', '1M_80p'], nargs=2,
        help=("CAN FD arbitration and data bitrate pair (e.g. -f 500k_80p 1M_80p), two of " + ', '.join(fd_bitrates.keys()))
    )
    parser.add_argument(
        '--ticktime',
        '-t',
        type=float,
        default=0,
        help=("If greater than zero, display 'tick' every this many seconds"),
    )
    args = parser.parse_args()
    return args


def main(argv=None):
    args = parse_args(argv)
    db = kvadblib.Dbc(filename=args.db)
    ch = canlib.openChannel(
        args.channel,
        flags=canlib.Open.CAN_FD,
        bitrate=fd_bitrates[args.fdbitrate[0].upper()],
        data_bitrate=fd_bitrates[args.fdbitrate[1].upper()],
    )
    ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
    ch.busOn()

    dbmonitor.monitor_channel(ch, db, args.ticktime)


if __name__ == '__main__':
    raise SystemExit(main())
