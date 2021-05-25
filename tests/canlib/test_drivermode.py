import os
import sys
# from pathlib import Path
from contextlib import contextmanager

import pytest
from kvprobe import features

from canlib import Frame, canlib
from canlib.canlib import Driver, Error

# Skip test module until BLB-1449 is merged
pytestmark = pytest.mark.skip


@contextmanager
def bus_control(ch):
    '''Ensures bus is on in a with statement and off afterwards.'''
    ch.busOn()
    try:
        yield ch
    finally:
        ch.busOff()


def is_old_driver(channel_no):
    old_driver = False
    chd = canlib.ChannelData(channel_no)
    driver_name = chd.driver_name

    old_linux = ['kvvirtualcan', 'pcican', 'pcicanII', 'usbcanII']
    old_windows = ['kcane', 'kcanh', 'kcans', 'kcanv', 'kcanx']
    old_drivers = old_linux + old_windows

    for name in old_drivers:
        if driver_name.find(name) > -1:
            old_driver = True
            break

    return old_driver


def is_linux():
    return sys.platform.startswith('linux')


def message_recieved(chsrc, chdst):
    """
    Tests if drivermode is silent or normal by sending a can Frame.
    """

    with bus_control(chsrc) as ch_src, bus_control(chdst) as ch_dst:
        inp_frame = Frame(id_=100, data=[0, 1, 2, 3], flags=canlib.MessageFlag.STD)

        # Write, wait
        try:
            ch_src.writeWait(inp_frame, timeout=100)
        except canlib.exceptions.CanError as e:
            if e.status == Error.TIMEOUT:
                return False
            else:
                raise

        # Read, wait
        try:
            outp_frame = ch_dst.read(timeout=100)
        except canlib.exceptions.CanError as e:
            if e.status != Error.TIMEOUT:
                raise
        else:
            return outp_frame == inp_frame

    return True


def test_mode_using_two_handles(channel_no):

    old_driver = is_old_driver(channel_no)

    # Does not work at all for old units on linux
    if old_driver and is_linux:
        pytest.skip()

    with canlib.openChannel(channel_no, canlib.Open.REQUIRE_INIT_ACCESS) as chA_1:

        chA_1.setBusOutputControl(Driver.SILENT)
        assert chA_1.getBusOutputControl() == Driver.SILENT

        with canlib.openChannel(channel_no, canlib.Open.NO_INIT_ACCESS) as chA_2:
            chA_2.report_access_errors = True
            assert chA_1.getBusOutputControl() == Driver.SILENT
            if not old_driver:
                assert chA_2.getBusOutputControl() == Driver.SILENT

            chA_1.setBusOutputControl(Driver.NORMAL)
            assert chA_1.getBusOutputControl() == Driver.NORMAL
            assert chA_2.getBusOutputControl() == Driver.NORMAL

            chA_1.setBusOutputControl(Driver.SILENT)
            assert chA_1.getBusOutputControl() == Driver.SILENT
            if not old_driver:
                assert chA_2.getBusOutputControl() == Driver.SILENT
        assert chA_1.getBusOutputControl() == Driver.SILENT

        # teardown, move to conftest later if this correct
        chA_1.setBusOutputControl(Driver.NORMAL)


def test_drivermode_persists_between_sessions(channel_no):

    if is_old_driver(channel_no):
        pytest.skip()

    with canlib.openChannel(channel_no, canlib.Open.REQUIRE_INIT_ACCESS) as chA_1:
        chA_1.setBusOutputControl(Driver.NORMAL)
        assert chA_1.getBusOutputControl() == Driver.NORMAL
        chA_1.setBusOutputControl(Driver.SILENT)
        assert chA_1.getBusOutputControl() == Driver.SILENT

    with canlib.openChannel(channel_no, canlib.Open.REQUIRE_INIT_ACCESS) as chA_1:
        assert chA_1.getBusOutputControl() == Driver.SILENT
        chA_1.setBusOutputControl(Driver.NORMAL)

    with canlib.openChannel(channel_no, canlib.Open.REQUIRE_INIT_ACCESS) as chA_1:
        assert chA_1.getBusOutputControl() == Driver.NORMAL


def test_mode_using_one_handle(channel_no):
    old_unit_linux = is_linux() and is_old_driver(channel_no)

    with canlib.openChannel(channel_no) as chA_1:

        chA_1.setBusOutputControl(Driver.SILENT)
        assert chA_1.getBusOutputControl() == Driver.SILENT

        # Do something to trigger a new channel to open (Linux)
        # ..which used to default the cached value for the channel to normal
        if not old_unit_linux:
            chd = canlib.ChannelData(channel_no)
            _ = chd.card_type

        assert chA_1.getBusOutputControl() == Driver.SILENT

        chA_1.setBusOutputControl(Driver.NORMAL)


def test_mode_using_two_handles_and_traffic(channel_no_pair):

    chNoA, chNoB = channel_no_pair[:2]

    with canlib.openChannel(chNoB, canlib.Open.REQUIRE_INIT_ACCESS) as chB:
        with canlib.openChannel(chNoA, canlib.Open.REQUIRE_INIT_ACCESS) as chA_1:
            # m32_firm has 3Mbit default bitrate (BLB-1582)
            chA_1.setBusParams(freq=canlib.canBITRATE_500K)
            chB.setBusParams(freq=canlib.canBITRATE_500K)

            chA_1.setBusOutputControl(Driver.NORMAL)
            chB.setBusOutputControl(Driver.NORMAL)

            assert message_recieved(chA_1, chB)

            chA_1.setBusOutputControl(Driver.SILENT)
            assert not message_recieved(chA_1, chB)

            with canlib.openChannel(chNoA, canlib.Open.NO_INIT_ACCESS) as chA_2:

                # m32_firm has 3Mbit default bitrate (BLB-1582)
                chA_2.setBusParams(freq=canlib.canBITRATE_500K)

                chA_2.report_access_errors = True
                assert not message_recieved(chA_1, chB)
                assert not message_recieved(chA_2, chB)

                chA_1.setBusOutputControl(Driver.NORMAL)
                assert chA_1.getBusOutputControl() == Driver.NORMAL
                assert message_recieved(chA_1, chB)
                assert message_recieved(chA_2, chB)

                chA_1.setBusOutputControl(Driver.SILENT)
                assert not message_recieved(chA_1, chB)
                assert not message_recieved(chA_2, chB)
            assert not message_recieved(chA_1, chB)

            chA_1.setBusOutputControl(Driver.NORMAL)


def test_mode_using_one_handle_and_traffic(channel_no_pair):
    chNoA, chNoB = channel_no_pair[:2]
    with canlib.openChannel(chNoB, canlib.Open.REQUIRE_INIT_ACCESS) as chB:
        with canlib.openChannel(chNoA) as chA:

            chA.setBusOutputControl(Driver.SILENT)
            assert not message_recieved(chA, chB)

            # Do something that trigger a new channel to open (Linux)
            chd = canlib.ChannelData(chNoA)
            _ = chd.card_type

            chA.setBusOutputControl(Driver.SILENT)
            assert not message_recieved(chA, chB)

            # teardown, move to conftest later if this correct
            chA.setBusOutputControl(Driver.NORMAL)


@pytest.mark.feature(features.script)
def test_mode_with_tscript(channel_no, datadir):
    scriptfile = os.path.join(datadir, "txe", "drivermode1.txe")
    slot = 0

    with canlib.openChannel(channel_no) as ch:
        ch.scriptLoadFile(slot, str(scriptfile))
        ch.scriptStart(slot)
        envvars = canlib.EnvVar(ch)

        # set normal
        ch.setBusOutputControl(Driver.NORMAL)
        assert ch.getBusOutputControl() == Driver.NORMAL

        # verify script normal
        ch.scriptSendEvent(eventNo=ord('g'))
        assert not envvars.ev_silent

        # set silent
        ch.setBusOutputControl(Driver.SILENT)
        assert ch.getBusOutputControl() == Driver.SILENT

        # verify script silent
        ch.scriptSendEvent(eventNo=ord('g'))
        assert envvars.ev_silent

        # set normal
        ch.setBusOutputControl(Driver.NORMAL)
        assert ch.getBusOutputControl() == Driver.NORMAL

        # set script silent
        ch.scriptSendEvent(eventNo=ord('s'))
        assert ch.getBusOutputControl() == Driver.SILENT

        # set script normal
        ch.scriptSendEvent(eventNo=ord('n'))
        assert ch.getBusOutputControl() == Driver.NORMAL

        ch.scriptStop(slot)
        ch.scriptUnload(slot)
