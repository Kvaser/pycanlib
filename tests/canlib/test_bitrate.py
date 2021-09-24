import pytest
from kvprobe import features

from canlib import canlib


def test_Bitrate(channel_no):
    ch = canlib.openChannel(channel_no, flags=0, bitrate=canlib.Bitrate.BITRATE_1M)
    expected_data = (1000000, 5, 2, 1, 1, 0)
    # We ignore the fields "noSamp" and "syncmode"
    assert ch.getBusParams()[:4] == expected_data[:4]
    ch.close()


@pytest.mark.feature(features.canfd)
def test_BitrateFD(channel_no):
    ch = canlib.openChannel(
        channel_no,
        flags=canlib.Open.CAN_FD,
        bitrate=canlib.BitrateFD.BITRATE_500K_80P,
        data_bitrate=canlib.BitrateFD.BITRATE_1M_80P,
    )
    expected_arb = (500000, 63, 16, 16, 1, 0)
    expected_data = (1000000, 31, 8, 8)
    # We ignore the fields "noSamp" and "syncmode"
    assert ch.getBusParams()[:4] == expected_arb[:4]
    # assert ch.getBusParams() == expected_arb
    assert ch.getBusParamsFd() == expected_data
    ch.close()
