"""script_snooper.py -- Print all output from selected scripts

This script uses canlib.canlib to print all output (printf() calls)
from t-script.

It requires a connected Kvaser device with t-script capability.

"""
import argparse
import time

from canlib import canlib

BITRATE = canlib.Bitrate.BITRATE_500K


def snoop_loop(channel, slots):
    with canlib.openChannel(channel, bitrate=BITRATE) as ch:
        if slots:
            for slot in slots:
                ch.scriptRequestText(slot)
        else:
            ch.scriptRequestText(canlib.ScriptRequest.ALL_SLOTS)

        if slots:
            print(
                "Listening on script slots {slots} via channel {channel}".format(
                    slots=slots, channel=channel
                )
            )
        else:
            print(
                "Listening on all script slots via channel {channel}".format(
                    slots=slots, channel=channel
                )
            )
        while True:
            try:
                text = ch.scriptGetText()
                print("script", text.slot, ':', text.rstrip('\n'), flush=True)
            except canlib.CanNoMsg:
                time.sleep(0.05)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Listen on a CAN channel and print all frames received."
    )
    parser.add_argument(
        'channel', type=int, default=0, nargs='?', help="CANlib channel to use to talk to device"
    )
    parser.add_argument(
        '-s',
        '--slot',
        type=int,
        default=[],
        nargs='+',
        help="Script slot(s) to listen to on the device. If omitted, will listen to all slots.",
    )
    args = parser.parse_args()

    try:
        snoop_loop(args.channel, args.slot)
    except KeyboardInterrupt:
        pass
