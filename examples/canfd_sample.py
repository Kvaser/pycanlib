"""canfd_sample.py -- Send a few frames using CAN FD

This script uses canlib.canlib to send some frames using the CAN FD standard
with different bitrates.

It requires two connected CANlib channels capable of CAN FD.

"""
import argparse

from canlib import Frame, canlib

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send some messages using CAN FD.")
    parser.add_argument(
        'channel_zero', type=int, default=0, nargs='?', help=("The channel to send messages on.")
    )
    parser.add_argument(
        'channel_one', type=int, default=1, nargs='?', help=("The channel to receive messages on.")
    )
    args = parser.parse_args()

    # Get clock frequency of device(s).
    clk_freq_0 = canlib.ChannelData(args.channel_zero).clock_info.frequency()
    clk_freq_1 = canlib.ChannelData(args.channel_one).clock_info.frequency()

    # Calculate bus parameters for CAN FD arbitration phase.
    bp_arbitration_0 = canlib.busparams.calc_busparamstq(
        target_bitrate=1000000,
        target_sample_point=80,
        target_sync_jump_width=20,
        clk_freq=clk_freq_0,
        prescaler=2,
    )

    # Calculate bus parameters for CAN FD data phase.
    # target_prop_tq must be 0 accordint to CAN FD standard.
    bp_data_0 = canlib.busparams.calc_busparamstq(
        target_bitrate=1000000,
        target_sample_point=80,
        target_sync_jump_width=20,
        clk_freq=clk_freq_0,
        target_prop_tq=0,
        prescaler=2,
    )

    bp_arbitration_1 = canlib.busparams.calc_busparamstq(
        target_bitrate=1000000,
        target_sample_point=80,
        target_sync_jump_width=20,
        clk_freq=clk_freq_1,
        prescaler=2,
    )

    bp_data_1 = canlib.busparams.calc_busparamstq(
        target_bitrate=1000000,
        target_sample_point=80,
        target_sync_jump_width=20,
        clk_freq=clk_freq_1,
        target_prop_tq=0,
        prescaler=2,
    )

    # Open two channels as CAN FD
    ch0 = canlib.openChannel(
        args.channel_zero,
        flags=canlib.Open.CAN_FD,
        bitrate=bp_arbitration_0,
        data_bitrate=bp_data_0,
    )
    ch1 = canlib.openChannel(
        args.channel_one,
        flags=canlib.Open.CAN_FD,
        bitrate=bp_arbitration_1,
        data_bitrate=bp_data_1,
    )

    ch0.busOn()
    ch1.busOn()

    # Send and receive a simple frame
    frame = Frame(id_=100, data=range(5))
    print('Sending:\n', frame)
    ch0.write(frame)
    frame = ch1.read(timeout=1000)
    print('Receiving:\n', frame)

    # Close the channels
    ch0.busOff()
    ch1.busOff()
    ch0.close()
    ch1.close()

    # Print an empty line for separation
    print()

    bp_arbitration_0 = canlib.busparams.calc_busparamstq(
        target_bitrate=500000,
        target_sample_point=80,
        target_sync_jump_width=20,
        clk_freq=clk_freq_0,
        prescaler=2,
    )

    bp_data_0 = canlib.busparams.calc_busparamstq(
        target_bitrate=2000000,
        target_sample_point=80,
        target_sync_jump_width=20,
        clk_freq=clk_freq_0,
        target_prop_tq=0,
        prescaler=2,
    )

    bp_arbitration_1 = canlib.busparams.calc_busparamstq(
        target_bitrate=500000,
        target_sample_point=80,
        target_sync_jump_width=20,
        clk_freq=clk_freq_1,
        prescaler=2,
    )

    bp_data_1 = canlib.busparams.calc_busparamstq(
        target_bitrate=2000000,
        target_sample_point=80,
        target_sync_jump_width=20,
        clk_freq=clk_freq_1,
        target_prop_tq=0,
        prescaler=2,
    )

    # Reopen the two channels as CAN FD, this time with bitrate 500K 80P and
    # data bitrate 2M 80P.
    ch0 = canlib.openChannel(
        args.channel_zero,
        flags=canlib.Open.CAN_FD,
        bitrate=bp_arbitration_0,
        data_bitrate=bp_data_0,
    )
    ch0.setBusOutputControl()
    ch1 = canlib.openChannel(
        args.channel_one,
        flags=canlib.Open.CAN_FD,
        bitrate=bp_arbitration_1,
        data_bitrate=bp_data_1,
    )
    ch1.setBusOutputControl()

    ch1.busOn()
    ch0.busOn()

    # Send and receive a slightly more complex frame
    frame = Frame(id_=100, data=range(64), dlc=64, flags=canlib.canFDMSG_BRS | canlib.canFDMSG_FDF)
    print('Sending:\n', frame)
    ch0.write(frame)

    frame = ch1.read(timeout=1000)
    print('Receiving:\n', frame)
