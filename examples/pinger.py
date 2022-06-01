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

# Create a dictionary of predefined CAN bitrates, using the name after
# "BITRATE_" as key. E.g. "500K".
bitrates = {x.name.replace("BITRATE_", ""): x for x in canlib.Bitrate}


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


def ping_loop(ch, db, num_messages, quantity, interval, seed=None):

    if seed is None:
        seed = 0
    else:
        try:
            seed = int(seed)
        except ValueError:
            seed = seed
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
            # If the channel is opened as CAN FD, we ignore messages in dbc
            # that is not marked as CAN FD. Similarily, if the channel is
            # opened as CAN, we inore messages in dbc that is marked as CAN FD.
            if ch.is_can_fd() != (canlib.MessageFlag.FDF in msg.canflags):
                continue
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


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Send random CAN message based on a database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
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
            "The seed used for choosing messages. If possible, will be converted to an int."
            " If no argument is given, a random seed will be used."
        ),
    )
    args = parser.parse_args()
    return args


def main(argv=None):
    args = parse_args(argv)
    db = kvadblib.Dbc(filename=args.db)

    ch = canlib.openChannel(args.channel, bitrate=bitrates[args.bitrate.upper()])
    ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
    ch.busOn()

    ping_loop(
        ch=ch,
        db=db,
        num_messages=args.num_messages,
        quantity=args.quantity,
        interval=args.interval,
        seed=args.seed,
    )


if __name__ == '__main__':
    raise SystemExit(main())
