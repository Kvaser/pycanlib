"""dbmonitor.py -- Read CAN messages using a database

This script will use canlib.canlib and canlib.kvadblib to monitor a CAN
channel, and look up all messages received in a database before printing them.

It requires a CANlib channel with a connected device capable of receiving CAN
messages, some source of CAN messages, and the same database that the source is
using to generate the messages.

In this example the channel is opened with flag canOPEN_ACCEPT_LARGE_DLC (optional).
This enables a DLC larger than 8 bytes (up to 15 for classic CAN). If
canOPEN_ACCEPT_LARGE_DLC is excluded, generated frames with DLC > 8, will attain
a DLC of 8 on the receiving end, which may compromise the DLC equivalence
check.

The source of the messages may be e.g. the pinger.py example script.

"""
import argparse

from canlib import canlib, kvadblib

# Create a dictionary of predefined CAN bitrates, using the name after
# "BITRATE_" as key. E.g. "500K".
bitrates = {x.name.replace("BITRATE_", ""): x for x in canlib.Bitrate}


def printframe(db, frame):
    try:
        bmsg = db.interpret(frame)
    except kvadblib.KvdNoMessage:
        print(f"<<< No message found for frame with id {frame.id} >>>")
        return

    if not bmsg._message.dlc == bmsg._frame.dlc:
        print(
            "<<< Could not interpret message because DLC does not match for"
            f" frame with id {frame.id} >>>"
        )
        print(f"\t- DLC (database): {bmsg._message.dlc}")
        print(f"\t- DLC (received frame): {bmsg._frame.dlc}")
        return

    msg = bmsg._message

    print('┏', msg.name)

    if msg.comment:
        print('┃', f'"{msg.comment}"')

    for bsig in bmsg:
        print('┃', bsig.name + ':', bsig.value, bsig.unit)

    print('┗')


def monitor_channel(ch, db, ticktime):

    timeout = 0.5
    tick_countup = 0
    if ticktime <= 0:
        ticktime = None
    elif ticktime < timeout:
        timeout = ticktime

    print("Listening...")
    while True:
        try:
            frame = ch.read(timeout=int(timeout * 1000))
            printframe(db, frame)
        except canlib.CanNoMsg:
            if ticktime is not None:
                tick_countup += timeout
                while tick_countup > ticktime:
                    print("tick")
                    tick_countup -= ticktime
        except KeyboardInterrupt:
            print("Stop.")
            break


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
        '--bitrate', '-b', default='500k', help=("Bitrate, one of " + ', '.join(bitrates.keys()))
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
    ch = canlib.openChannel(args.channel, canlib.canOPEN_ACCEPT_LARGE_DLC, bitrates[args.bitrate.upper()])
    ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
    ch.busOn()

    monitor_channel(ch, db, args.ticktime)


if __name__ == '__main__':
    raise SystemExit(main())
