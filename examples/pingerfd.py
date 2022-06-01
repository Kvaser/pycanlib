"""pingerfd.py -- Send random CAN FD messages based on a database

This script uses canlib.canlib and canlib.kvadblib to send random messages from
a database with random data.

The script also reuses the ping_loop function defined in pinger.py

It requires a CANlib channel a connected device capable of sending CAN
messages, something that receives those messages, and a database to inspect for
the messages to send.

Messages can be received and printed by e.g. the dbmonitorfd.py example script.

"""
import argparse
import random
import time

from canlib import canlib, kvadblib

import pinger

# Create a dictionary of predefined CAN FD bitrates, using the name after
# "BITRATE_" as key. E.g. "500K_80P".
fd_bitrates = {x.name.replace("BITRATE_", ""): x for x in canlib.BitrateFD}


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Send random CAN FD message based on a database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        'channel', type=int, default=0, nargs='?', help=("The channel to send messages on.")
    )
    parser.add_argument(
        '--fdbitrate', '-f', default=['500k_80p', '1M_80p'], nargs=2,
        help=("CAN FD arbitration and data bitrate pair (e.g. -f 500k_80p 1M_80p), two of " + ', '.join(fd_bitrates.keys()))
    )
    parser.add_argument(
        '--db', default="engine_example.dbc", help=("The database file to base messages on.")
    )
    parser.add_argument(
        '-Q', '--quantity', type=int, default=5, help=("The number of signals to send each tick.")
    )
    parser.add_argument(
        '-I', '--interval', type=float, default=0.2, help=("The time, in seconds, between ticks.")
    )
    parser.add_argument(
        '-n',
        '--num-messages',
        type=int,
        default=-1,
        help=("The number of message from the database to use, or -1 to use all."),
    )
    parser.add_argument(
        '-s',
        '--seed',
        nargs='?',
        default='0',
        help=(
            "The seed used for choosing messages. If possible, will be converted to an int. If no argument is given, a random seed will be used."
        ),
    )
    args = parser.parse_args()

    if args.seed is not None:
        try:
            args.seed = int(args.seed)
        except ValueError:
            args.seed = args.seed
    return args


def main(argv=None):
    args = parse_args(argv)
    db = kvadblib.Dbc(filename=args.db)
    print(f"{args.channel=}, {fd_bitrates[args.fdbitrate[0].upper()]=}, {fd_bitrates[args.fdbitrate[1].upper()]=}")
    ch = canlib.openChannel(
        args.channel,
        flags=canlib.Open.CAN_FD,
        bitrate=fd_bitrates[args.fdbitrate[0].upper()],
        data_bitrate=fd_bitrates[args.fdbitrate[1].upper()],
    )
    ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
    ch.busOn()

    pinger.ping_loop(
        ch=ch,
        db=db,
        num_messages=args.num_messages,
        quantity=args.quantity,
        interval=args.interval,
        seed=args.seed,
    )


if __name__ == '__main__':
    raise SystemExit(main())
