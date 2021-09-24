import sys
import time

import pytest
from conftest import winonly

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
        ch.set_callback(callback, context=121, event=canlib.Notify.BUSONOFF)
        ch.busOn()
        time.sleep(0.5)
        assert callback_has_been_called
        callback_has_been_called = False
        print('Waiting...')
        ch.busOff()
        time.sleep(0.5)
        assert callback_has_been_called


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
        time.sleep(0.5)
        assert callback_status_has_been_called
        with pytest.raises(canlib.CanError) as excinfo:
            ch.writeWait(Frame(id_=4, data=b'10'), timeout=1000)
        assert excinfo.value.status == -7
        time.sleep(0.5)
        assert callback_error_has_been_called
        callback_status_has_been_called = False
        print('Waiting...')
        ch.busOff()
        time.sleep(0.5)

        # Fails in Windows fb:24233
        if not sys.platform.startswith('win'):
            assert callback_status_has_been_called


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

    with canlib.openChannel(CHANNEL) as ch:
        ch.set_callback(callback, context=121, event=canlib.Notify.RX)
        ch.busOn()
        with canlib.openChannel(CHANNEL_TWO) as ch2:
            ch2.busOn()
            assert not callback_rx_has_been_called
            assert not callback_tx_has_been_called
            ch2.writeWait(Frame(id_=4, data=b'10'), timeout=1000)
            time.sleep(0.5)
            assert callback_rx_has_been_called
            assert not callback_tx_has_been_called
            frame = ch.read()
            print(frame)
            callback_rx_has_been_called = False

            ch.set_callback(callback, context=120, event=canlib.Notify.NONE)
            ch2.set_callback(callback, context=122, event=canlib.Notify.TX)
            ch2.writeWait(Frame(id_=5, data=b'10'), timeout=1000)
            time.sleep(0.5)
            assert not callback_rx_has_been_called
            assert callback_tx_has_been_called
            frame = ch.read()
            print(frame)
            ch.set_callback(callback, context=121, event=canlib.Notify.NONE)
