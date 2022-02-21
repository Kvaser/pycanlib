import pytest

from kvprobe import features
from canlib import canlib


@pytest.mark.feature(features.canfd)
def test_is_can_fd_true(channel_no):
    with canlib.Channel(channel_no, flags=canlib.Open.CAN_FD) as ch_a, \
            canlib.Channel(channel_no, flags=canlib.Open.NO_INIT_ACCESS) as ch_b:
        assert ch_a.is_can_fd() == ch_b.is_can_fd()
        assert ch_a.is_can_fd() is True


def test_is_can_fd_false(channel_no):
    with canlib.Channel(channel_no, flags=canlib.Open.EXCLUSIVE) as ch_a:
        with canlib.Channel(
            channel_no,
            flags=canlib.Open.NO_INIT_ACCESS | canlib.Open.OVERRIDE_EXCLUSIVE
        ) as ch_b:
            assert ch_a.is_can_fd() == ch_b.is_can_fd()
            assert ch_a.is_can_fd() is False
