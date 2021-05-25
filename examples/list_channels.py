"""list_channels.py -- List all CANlib channel

This script uses canlib.canlib to list all CANlib channels and information
about the device that is using them.

"""
import argparse

from canlib import canlib


def print_channels():
    for ch in range(canlib.getNumberOfChannels()):
        chdata = canlib.ChannelData(ch)
        print(
            "{ch}. {name} ({ean} / {serial})".format(
                ch=ch,
                name=chdata.channel_name,
                ean=chdata.card_upc_no,
                serial=chdata.card_serial_no,
            )
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="List all CANlib channels and information about them."
    )
    args = parser.parse_args()

    print_channels()
