"""pinger.py -- Send random CAN messages based on a database

This script uses canlib.canlib and canlib.kvadblib to send random messages from
a database with random data.

It requires a CANlib channel a connected device capable of sending CAN
messages, something that receives those messages, and a database to inspect for
the messages to send.

Messages can be received and printed by e.g. the dbmonitor.py example script.

"""
import argparse
import random
import time

from canlib import canlib, kvadblib

bitrates = {
    '1M': canlib.Bitrate.BITRATE_1M,
    '500K': canlib.Bitrate.BITRATE_500K,
    '250K': canlib.Bitrate.BITRATE_250K,
    '125K': canlib.Bitrate.BITRATE_125K,
    '100K': canlib.Bitrate.BITRATE_100K,
    '62K': canlib.Bitrate.BITRATE_62K,
    '50K': canlib.Bitrate.BITRATE_50K,
    '83K': canlib.Bitrate.BITRATE_83K,
    '10K': canlib.Bitrate.BITRATE_10K,
}


def set_random_framebox_signal(db, framebox, signals):
    sig = random.choice(signals)
    value = get_random_value(db, sig)
    framebox.signal(sig.name).phys = value


def get_random_value(db, sig):
    limits = sig.limits
    value = random.uniform(limits.min, limits.max)

    # round value depending on type...
    if sig.type is kvadblib.SignalType.UNSIGNED or sig.type is kvadblib.SignalType.SIGNED:
        # ...remove decimals if the signal was of type unsigned
        value = int(round(value))
    else:
        # ...otherwise, round to get only one decimal
        value = round(value, 1)

    return value


def ping_loop(channel_number, db_name, num_messages, quantity, interval, bitrate, seed=0):
    db = kvadblib.Dbc(filename=db_name)

    ch = canlib.openChannel(channel_number, bitrate=bitrate)
    ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
    ch.busOn()

    random.seed(seed)

    if num_messages == -1:
        used_messages = list(db)
    else:
        used_messages = random.sample(list(db), num_messages)

    print()
    print("Randomly selecting signals from the following messages:")
    print(used_messages)
    print("Seed used was " + repr(seed))
    print()

    while True:
        # Create an empty framebox each time, ignoring previously set signal
        # values.
        framebox = kvadblib.FrameBox(db)

        # Add all messages to the framebox, as we may use send any signal from
        # any of them.
        for msg in db:
            framebox.add_message(msg.name)

        # Make a list of all signals (which framebox has found in all messages
        # we gave it), so that set_random_framebox_signal() can pick a random
        # one.
        signals = [bsig.signal for bsig in framebox.signals()]

        # Set some random signals to random values
        for i in range(quantity):
            set_random_framebox_signal(db, framebox, signals)

        # Send all messages/frames
        for frame in framebox.frames():
            print('Sending frame', frame)
            ch.writeWait(frame, timeout=5000)

        time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send random CAN message based on a database.")
    parser.add_argument(
        'channel', type=int, default=0, nargs='?', help=("The channel to send messages on.")
    )
    parser.add_argument(
        '--bitrate', '-b', default='500k', help=("Bitrate, one of " + ', '.join(bitrates.keys()))
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

    if args.seed is None:
        seed = None
    else:
        try:
            seed = int(args.seed)
        except ValueError:
            seed = args.seed

    ping_loop(
        channel_number=args.channel,
        db_name=args.db,
        num_messages=args.num_messages,
        quantity=args.quantity,
        interval=args.interval,
        bitrate=bitrates[args.bitrate.upper()],
        seed=args.seed,
    )
