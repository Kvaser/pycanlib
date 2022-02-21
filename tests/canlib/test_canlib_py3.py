import sys
import time

import pytest
from conftest import winonly, wait_until

from canlib import Frame, canlib

# This file contains tests of canlib that cannot be run in Python 2.7 due to
# syntax errors.


def test_notify_callback_buson(channel_no):
    callback_has_been_called = False

    def callback_func(hnd, context, event):
        event = canlib.Notify(event)
        nonlocal callback_has_been_called
        print(f"Callback function called, context:{context}, event:{event!r}")
        callback_has_been_called = True

    callback = canlib.dll.KVCALLBACK_T(callback_func)

    with canlib.openChannel(channel_no) as ch:
        ch.busOff()
        ch.set_callback(callback, context=121, event=canlib.Notify.BUSONOFF)
        ch.busOn()
        assert wait_until(lambda: callback_has_been_called, 1.0)
        callback_has_been_called = False
        print('Waiting...')
        ch.busOff()
        assert wait_until(lambda: callback_has_been_called, 1.0)


@winonly
def test_notify_callback_errorstatus(channel_no):
    callback_status_has_been_called = False
    callback_error_has_been_called = False

    def callback_func(hnd, context, event):
        event = canlib.Notify(event)
        nonlocal callback_status_has_been_called
        nonlocal callback_error_has_been_called
        print(f"Callback function called, context:{context}, event:{event!r}")
        if event == canlib.Notify.STATUS:
            callback_status_has_been_called = True
        elif event == canlib.Notify.ERROR:
            callback_error_has_been_called = True
        else:
            assert 0

    callback = canlib.dll.KVCALLBACK_T(callback_func)

    with canlib.openChannel(channel_no) as ch:
        assert not callback_status_has_been_called
        ch.set_callback(callback, context=131, event=canlib.Notify.STATUS | canlib.Notify.ERROR)
        assert not callback_error_has_been_called
        assert not callback_status_has_been_called
        ch.busOn()
        assert wait_until(lambda: callback_status_has_been_called, 1.0)
        with pytest.raises(canlib.CanError) as excinfo:
            ch.writeWait(Frame(id_=4, data=b'10'), timeout=1000)
        assert excinfo.value.status == -7
        assert wait_until(lambda: callback_error_has_been_called, 1.0)
        callback_status_has_been_called = False
        print('Waiting...')
        ch.busOff()
        # Fails in Windows fb:24233
        if not sys.platform.startswith('win'):
            assert wait_until(lambda: callback_status_has_been_called, 1.0)


def test_notify_callback_rxtx(channel_no_pair):
    CHANNEL, CHANNEL_TWO = channel_no_pair
    callback_rx_has_been_called = False
    callback_tx_has_been_called = False

    def callback_func(hnd, context, event):
        event = canlib.Notify(event)
        nonlocal callback_rx_has_been_called
        nonlocal callback_tx_has_been_called
        print(f"Callback function called, context:{context}, event:{event!r}")
        if context == 121:
            callback_rx_has_been_called = True
        elif context == 122:
            callback_tx_has_been_called = True

    callback = canlib.dll.KVCALLBACK_T(callback_func)

    with canlib.openChannel(CHANNEL, bitrate=canlib.Bitrate.BITRATE_1M ) as ch:
        ch.set_callback(callback, context=121, event=canlib.Notify.RX)
        ch.setBusOutputControl(canlib.Driver.NORMAL)
        ch.busOn()
        with canlib.openChannel(CHANNEL_TWO, bitrate=canlib.Bitrate.BITRATE_1M) as ch2:
            ch2.setBusOutputControl(canlib.Driver.NORMAL)
            ch2.busOn()
            assert not callback_rx_has_been_called
            assert not callback_tx_has_been_called
            ch2.writeWait(Frame(id_=4, data=b'10'), timeout=1000)
            assert wait_until(lambda: callback_rx_has_been_called, 1.0)
            assert not callback_tx_has_been_called
            frame = ch.read()
            callback_rx_has_been_called = False
            ch.set_callback(callback, context=120, event=canlib.Notify.NONE)
            ch2.set_callback(callback, context=122, event=canlib.Notify.TX)
            ch2.writeWait(Frame(id_=5, data=b'10'), timeout=1000)
            assert wait_until(lambda: callback_tx_has_been_called, 1.0)
            assert not callback_rx_has_been_called
            frame = ch.read()
            ch.set_callback(callback, context=121, event=canlib.Notify.NONE)
