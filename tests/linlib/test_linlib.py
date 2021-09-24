import pytest

from canlib import Frame, VersionNumber, canlib, linlib
from canlib.ean import EAN


def check_messages(channel, number, print_as=None):
    """Retrieves all messages from channel, and asserts there were `number` messages

    If `print_as` is truthy, all messages are printed with a header in the
    format ~"{print_as} received:"~.

    """
    if print_as:
        print(str(print_as) + " received:")
    for _ in range(number):
        frame = channel.read(timeout=100)
        print(frame)
        assert frame.dlc > 0
        assert not (frame.flags & linlib.MessageFlag.NODATA)
    with pytest.raises(linlib.LinNoMessageError):
        channel.read(timeout=10)


def test_version():
    try:
        v = linlib.dllversion()
        print(v)
        print(v.major, v.minor)
    except NotImplementedError:
        # Accessing LINlib version requires CANlib SDK v5.23 or newer.
        pass


class TestNamedtuples:
    # All instantiations here have small integers, regardless of the type they
    # should have.

    def test_TransceiverData(self):
        k = linlib.TransceiverData(ean=1, serial=2, type=3)
        p = linlib.TransceiverData(1, 2, 3)
        assert k == p

    def test_FirmwareVersion(self):
        k = linlib.FirmwareVersion(boot_version=1, app_version=2)
        p = linlib.FirmwareVersion(1, 2)
        assert k == p


def test_reinit_library():
    linlib.unloadLibrary()
    linlib.initializeLibrary()


def test_getChannelData(lin_no):
    ver_nums = linlib.getChannelData(lin_no)
    print(ver_nums)
    assert isinstance(ver_nums, VersionNumber)
    assert len(ver_nums) == 3
    assert all(isinstance(n, int) for n in ver_nums)


def test_getTransceiverData(lin_no):
    tdata = linlib.getTransceiverData(lin_no)
    print(tdata)
    ean, serial, ttype = tdata
    assert isinstance(ean, EAN)
    assert isinstance(serial, int)
    assert isinstance(ttype, canlib.TransceiverType)


def test_channel_basics(master):
    ch = master
    print(ch.getCanHandle())
    try:
        ver = ch.getFirmwareVersion()
    except linlib.LinNotImplementedError:
        pass
    else:
        print(ver)
        boot_ver, app_ver = ver
        assert len(boot_ver) == len(app_ver) == 3
        assert all(isinstance(n, int) for n in boot_ver)
        assert all(isinstance(n, int) for n in app_ver)

    ch.setBitrate(10 ** 4)

    ch.busOn()

    ch.setupLIN(bps=10 ** 4)

    ch.writeSync(10 ** 2)

    ch.writeWakeup()

    ch.busOff()


def test_hear_self(master):
    # The data to be sent.
    data = Frame(id_=0, data=[1, 2, 3, 4, 5, 6, 7, 8])

    # the `Frame`'s `flags` attribute is not used when sending LIN messages,
    # however it will get a value (`MessageFlag.TX`) when we read the message
    # back. We set this flag on the original frame as well, so that we can
    # check equality later
    data.flags = linlib.MessageFlag.TX

    # Go on bus
    master.busOn()
    # Send a message
    master.writeMessage(data)

    # Read the message back
    read_data = master.read(timeout=100)

    assert data == read_data


def test_send_messages(master, slave):
    # go bus on
    master.busOn()
    slave.busOn()

    # Send five messages from master
    NUM_MESSAGES = 1
    for i in range(NUM_MESSAGES):
        master.writeMessage(Frame(id_=i, data=[1, 2, 3, 4, 5, 6, 7, 8]))
    master.writeSync(50)

    # make sure all messages have been received
    check_messages(slave, NUM_MESSAGES, "Slave")
    # the master should also have recorded them
    check_messages(master, NUM_MESSAGES, "Master")

    # go bus off
    master.busOff()
    slave.busOff()


def test_slave_response(master, slave):
    # go bus on
    master.busOn()
    slave.busOn()

    # Add a response to the slave
    slave.updateMessage(Frame(id_=23, data=[1, 2, 3, 4, 5, 6, 7, 8]))

    # No-one should have a message by this point
    with pytest.raises(linlib.LinNoMessageError):
        slave.read()
    with pytest.raises(linlib.LinNoMessageError):
        master.read()

    # Ask for the response
    master.requestMessage(23)

    master.writeSync(50)

    print("master:", master.read(timeout=100))
    print("slave:", slave.read(timeout=100))


def test_as_linlibtest(master, slave):
    ID = 0x17
    DATA = bytearray([1, 2, 3, 4])
    master.busOn()
    slave.busOn()

    # setup a message
    slave.updateMessage(Frame(id_=ID, data=DATA))
    with pytest.raises(linlib.LinNoMessageError):
        master.read(10)

    # request the message and check that it arrived
    master.requestMessage(ID)
    print(master.read(timeout=100))

    # only one message should have arrived
    with pytest.raises(linlib.LinNoMessageError):
        master.read(10)

    # request the message again, and see that we get it again
    master.requestMessage(ID)
    frame = master.read(timeout=100)
    print(frame)
    # flags will be different, so we can't compare the whole frame
    assert frame.id == ID
    assert frame.data == DATA

    # clear the message
    slave.clearMessage(0x17)
    # we should now get an empty message
    master.requestMessage(0x17)
    frame = master.read(timeout=100)
    print(frame)
    assert frame.id == ID
    assert not frame.data
    assert frame.flags & linlib.MessageFlag.NODATA

    # setup an intentionally corrupt message
    slave.updateMessage(Frame(id_=ID, data=DATA))
    slave.setupIllegalMessage(
        ID,
        disturb_flags=linlib.MessageDisturb.PARITY | linlib.MessageDisturb.CSUM,
        delay=0,
    )
    # we should now get a corrupt message
    master.requestMessage(0x17)
    frame = master.read(timeout=100)
    print(frame)
    assert frame.id == ID
    assert frame.flags & linlib.MessageFlag.PARITY_ERROR
    assert frame.flags & linlib.MessageFlag.CSUM_ERROR

    master.busOff()
    slave.busOff()


def test_wakeup(master, slave):
    def _both_have_wakup(ch1, ch2):
        for ch in ch1, ch2:
            frame = ch.read(timeout=100)
            print(frame)
            assert frame.flags & linlib.MessageFlag.WAKEUP_FRAME

    def _none_have_message(ch1, ch2):
        for ch in ch1, ch2:
            with pytest.raises(linlib.LinNoMessageError):
                ch.read()

    master.busOn()
    slave.busOn()

    # No-one should have a message by this point
    _none_have_message(master, slave)

    master.writeWakeup()

    _both_have_wakup(master, slave)
    _none_have_message(master, slave)

    slave.writeWakeup()

    _both_have_wakup(master, slave)
    _none_have_message(master, slave)


@pytest.mark.skip(reason="Never succeeds, check manually that it's 'better'")
def test_writeSync(master, slave):
    master.busOn()
    slave.busOn()

    for _ in range(10):
        master.writeMessage(Frame(id_=1, data=[0, 1, 2, 3]))
    master.writeSync(100)
    # Having writeSync() means more messages get through, but not all. So
    # comment this out and check that very few messages get printed in the loop below.

    print("-1", slave.read(timeout=100))
    for i in range(10 - 1):
        print(i, slave.read())


def test_lin_channel_flags(lin_no):
    channeldata = canlib.ChannelData(lin_no)
    print('card_upc_no', '->', repr(channeldata.card_upc_no))
    print('channel_flags', '->', repr(channeldata.channel_flags))
    # Flags are remembered, so we can't test this now...
    # assert channeldata.channel_flags == 0

    print(f'Opening channel {lin_no} as LIN master')
    master = linlib.openMaster(lin_no)
    assert channeldata.channel_flags == (
        canlib.ChannelFlags.IS_OPEN
        | canlib.ChannelFlags.IS_LIN_MASTER
        | canlib.ChannelFlags.IS_LIN
    )
    master.close()
    assert channeldata.channel_flags == (
        canlib.ChannelFlags.IS_LIN_MASTER | canlib.ChannelFlags.IS_LIN
    )

    print(f'Opening channel {lin_no} as LIN slave')
    slave = linlib.openSlave(lin_no)
    assert channeldata.channel_flags == (
        canlib.ChannelFlags.IS_OPEN | canlib.ChannelFlags.IS_LIN_SLAVE | canlib.ChannelFlags.IS_LIN
    )
    slave.close()
    assert channeldata.channel_flags == (
        canlib.ChannelFlags.IS_LIN_SLAVE | canlib.ChannelFlags.IS_LIN
    )
