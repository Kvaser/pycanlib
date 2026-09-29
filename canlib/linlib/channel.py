import ctypes as ct
from collections import namedtuple

from .. import deprecation, VersionNumber
from .. import canlib
from ..frame import LINFrame
from .enums import ChannelType, MessageFlag, Setup
from .structures import MessageInfo
from .wrapper import dll

FirmwareVersion = namedtuple('FirmwareVersion', 'boot_version app_version')


def openChannel(channel_number, channel_type, bps=None):
    """Open a channel to a LIN interface.

    Args:
        channel_number (`int`): The number of the channel. This is the same
            channel number as used by `.canlib.openChannel`.
        channel_type (`ChannelType`): Whether the LIN interface will be a
            master or slave.
        bps (`int` or `None`): If not `None`, `Channel.setBitrate` will be called with
            this value before the channel is returned.

    Returns:
        (`Channel`): The opened channel

    Note:
        For DRV Lin: The cable must be powered and connected to a LAPcan channel.
        For Kvaser LIN Leaf: The Leaf must be powered from the LIN side.

    """
    handle = dll.linOpenChannel(channel_number, channel_type)
    channel = Channel(handle)
    if bps is not None:
        channel.setBitrate(bps)
    return channel


def openMaster(channel_number, bps=None):
    """Open a channel as a master

    This function simply calls `openChannel` with `channel_type` set to
    `ChannelType.MASTER`.

    """
    return openChannel(channel_number, ChannelType.MASTER, bps=bps)


def openSlave(channel_number, bps=None):
    """Open a channel as a slave

    This function simply calls `openChannel` with `channel_type` set to
    `ChannelType.SLAVE`.

    """
    return openChannel(channel_number, ChannelType.SLAVE, bps=bps)


class Channel:
    """A LINlib channel

    This class is normally instantiated with `openMaster` or `openSlave`.

    Channels are automatically closed on garbage collection, and can
    also be used as context managers in which case they close as soon as the
    context exits.

    """

    def __init__(self, handle):
        self.handle = handle

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    # def readTimer():
    #     raise NotImplementedError

    def busOff(self):
        """Go bus off

        This function deactivates the LIN interface. It will not participate
        further in the LIN bus traffic.

        """
        dll.linBusOff(self.handle)

    def busOn(self):
        """Go bus on

        This function activates the LIN interface.

        """
        dll.linBusOn(self.handle)

    def clearMessage(self, msg_id):
        """Clear a message buffer for a LIN slave

        The message buffer will not answer next time it is polled.

        """
        dll.linClearMessage(self.handle, msg_id)

    def close(self):
        """Close this LINlib channel

        Closes an open handle to a LIN channel.

        Note:

            It is normally not necessary to call this function directly, as the
            internal handle is automatically closed when the `Channel` object
            is garbage collected.

        .. versionadded:: 1.6

        """
        if self.handle is not None:
            self.busOff()
            dll.linClose(self.handle)
            self.handle = None

    def get_can_channel(self):
        """Return the CAN Channel used by this LIN Channel

        Note:

            Since the returned `.canlib.Channel` is owned and controlled
            by linlib, this function should be used with great care.

        .. versionadded:: 1.20

        """
        can_hnd = ct.c_uint()
        dll.linGetCanHandle(self.handle, ct.byref(can_hnd))
        # The returned Channel contains a copy of the CAN handle owned and used
        # by linlib, so the user should not be allowed to close the underlying
        # CAN handle.
        return canlib.Channel._from_handle(can_hnd.value, allow_close=False)

    @deprecation.deprecated.favour("get_can_channel")
    def getCanHandle(self):
        """Return the CAN handle given an open LIN handle

        .. deprecated:: 1.20
           Use `.get_can_channel` instead.

        """
        can_handle = ct.c_uint()
        dll.linGetCanHandle(self.handle, ct.byref(can_handle))
        return can_handle.value

    def getFirmwareVersion(self):
        """Retrieve the firmware version from the LIN interface

        Returns a `FirmwareVersion` namedtuple containing `boot_version` and
        `app_version` that are `canlib.VersionNumber` namedtuples. If only one of
        these is needed, the return value can be unpacked as such::

            boot_ver, app_ver = channel.getFirmwareVersion()

        Note:
            For newer interfaces use `getChannelData` with
            `ChannelData.CARD_FIRMWARE_REV` instead.

            The version numbers aren't valid until `Channel.busOn` has been
            called.

            The firmware in the LIN interface is divided into two parts, the
            boot code and the application. The boot code is used only when
            reprogramming (reflashing) the LIN interface. The application
            handles all LIN communication.

            Version numbers are, since the precambric era, divided into a major
            version number, a minor version number and a build
            number. These are usually written like, for example,
            3.2.12. Here the major number is 3, the minor number 2 and the
            build number 12.

        """
        bootver = [ct.c_ubyte() for i in range(3)]
        appver = [ct.c_ubyte() for i in range(3)]

        # In Python 2, you can't use '*' on more than one argument
        refs = tuple(ct.byref(ub) for ub in bootver) + tuple(ct.byref(ub) for ub in appver)
        dll.linGetFirmwareVersion(self.handle, *refs)
        bootver = [v.value for v in bootver]
        appver = [v.value for v in appver]
        return FirmwareVersion(
            boot_version=VersionNumber(*bootver),
            app_version=VersionNumber(*appver),
        )

    def read(self, timeout=0):
        """Read a message from the LIN interface

        If a message is available for reception, linOK is returned. This is a
        non-blocking call. It waits until a message is received in the LIN
        interface, or the specified timeout period elapses.

        This may return a frame sent by `writeMessage` or `writeWakeup`.

        Note:
            This call will also return echoes of what the LIN interface is
            transmitting with `writeMessage`. In other words, the LIN
            interface can hear itself.

        Args:
            timeout (`int`): Timeout in milliseconds.

        Returns:
            (`canlib.LINFrame`)

        """
        id_ = ct.c_uint()
        _MAX_SIZE = 8
        msg = ct.create_string_buffer(_MAX_SIZE)
        dlc = ct.c_uint()
        flags = ct.c_uint()
        info = MessageInfo()

        dll.linReadMessageWait(
            self.handle,
            ct.byref(id_),
            ct.byref(msg),
            ct.byref(dlc),
            ct.byref(flags),
            ct.byref(info),
            timeout,
        )

        length = min(_MAX_SIZE, dlc.value)
        return LINFrame(
            id_=id_.value,
            data=bytearray(msg.raw[:length]),
            dlc=dlc.value,
            flags=MessageFlag(int(flags.value)),  # in Python 2, we get a long
            info=info,
        )

    def requestMessage(self, msgid):
        """Request a message from a slave

        This function writes a LIN message header to the LIN bus. A slave in
        the system is then expected to fill in the header with data.

        Note:
            This call is only available in master mode.

        """
        dll.linRequestMessage(self.handle, msgid)

    def setBitrate(self, bps):
        """Set the bitrate in bits per second

        This function sets the bit rate for a master, or the initial bit rate
        for a slave. The LIN interface should not be on-bus when this function
        is called.

        Note:
            The LIN Interface should not be on bus.
            Supported bit rates are 1000 - 20000 bits per second.

        """
        assert 1000 <= bps <= 20000  # qqqdaca nicer error
        dll.linSetBitrate(self.handle, bps)

    def setupIllegalMessage(self, msgid, disturb_flags, delay):
        """Create a corrupted LIN message

        Using this function, it is possible to use the LIN interface to create
        corrupted LIN messages. You call the function once for each LIN
        identifier that should be affected.

        To return to normal mode, either restart the LIN interface (by going
        off bus and on the bus again) or call the function with delay and
        disturb_flags set to zero.

        Args:

            msgid (`int`): The identifier of the LIN message

            disturb_flags (`MessageDisturb`): One or more of the
                `MessageDisturb` flags.

            delay (`int`): The delay parameter will result in a delay of this
                many bittimes after the header and before the first data byte.

        Note:
            The LIN Interface must be on bus for this command to work.
            It is supported in firmware version 2.4.1 and later.

        """
        dll.linSetupIllegalMessage(self.handle, msgid, disturb_flags, delay)

    def setupLIN(self, flags=Setup.VARIABLE_DLC, bps=0):
        """Setup the LIN interface

        This function changes various settings on a LIN Interface that is on
        bus. When going on bus, the bit rate and the flag values listed below
        are set to the default value (either as hard-coded in the firmware, or
        as stored in the non-volatile memory of the LIN Interface).

        With this function, you can do one or more of the following things:

        * Select checksum according to LIN 2.0

        * Turn variable message length off. The message length then will depend
          on the message ID.

        In master mode it is also possible to change the bit rate without going
        off bus first.

        Note:
            The LIN Interface must be on bus for this command to work.
            It is supported in firmware version 2.5.1 and later.
            For LIN 2.0 compliance, you must specify both LIN_ENHANCED_CHECKSUM
            and LIN_VARIABLE_DLC.

        Args:

            flags (`Setup`): One or more of the `Setup` flags

            bps (`int`): The bit rate in bits per second. This parameter can be
                used only in master mode. The bit rate is set without going off
                bus.

        """
        dll.linSetupLIN(self.handle, flags, bps)

    def updateMessage(self, frame):
        """Update a message buffer in a slave

        This function updates a message buffer in a slave. The contents of the
        message buffer will be used the next time the slave is polled for the
        specified LIN message id.

        Note:
            The LIN Interface must be on bus.

        Args:

            frame (`canlib.Frame`): The information to be updated. Only the `.Frame.id`,
                `.Frame.data`, and `.Frame.dlc` attributes are used. Note that the frame can,
                but not need not, be a `.LINFrame`.

        """
        void_p_data = (ct.c_ubyte * frame.dlc)(*frame.data)
        dll.linUpdateMessage(self.handle, frame.id, void_p_data, frame.dlc)

    def writeMessage(self, frame):
        """Write a LIN message

        Write a LIN message. It is advisable to wait until the message is
        echoed by `read` before transmitting a new message, or in
        case of a schedule table being used, transmit the next message when the
        previous one is known to be complete.

        Note:
            Only available in master mode

        Args:

            frame (`canlib.Frame`) :: The information to be updated. Only the `.Frame.id`,
                `.Frame.data`, and `.Frame.dlc` attributes are used. Note that the frame can,
                but not need not, be a `.LINFrame`.

        """
        void_p_data = (ct.c_ubyte * frame.dlc)(*frame.data)
        dll.linWriteMessage(self.handle, frame.id, void_p_data, frame.dlc)

    def writeSync(self, timeout):
        """Make sure all message transmitted to the interface have been received

        *timeout* is in milliseconds.

        When messages are transmitted to the LIN Interface, they are queued by
        the driver before appearing on the CAN bus.

        If the LIN Interface is in master mode and a LIN message has been
        transmitted with `writeMessage`, this function will return when the LIN
        Interface has received the message. If another LIN message is being
        received or transmitted, the message will not be transmitted on the LIN
        bus at once. And even if the LIN Interface is idle, the header of the
        new message will just have been started when `writeSync` returns.

        After calling `updateMessage` and `clearMessage` for a slave, this
        function is enough to know that the LIN Interface is updated.

        After `writeMessage`, it is advisable to wait until the message is
        echoed by `read` before transmitting a new message, or in case
        of a schedule table being used, transmit the next message when the
        previous one is known to be complete.

        When, in master mode, a message should be transmitted after a poll
        (reception) is done, it might be necessary to call `writeMessage`
        before the result is received via `read` as the LIN Interface
        waits up to the maximum frame length before knowing a received message
        is complete. A new message to transmit will force completion if the
        currently received one.

        """
        dll.linWriteSync(self.handle, timeout)

    def writeWakeup(self, count=0, interval=1):
        """Write one or more wakeup frames

        If *count* is zero (the default), one single wakeup frame is
        transmitted. If *count* > 1, several wakeup frames are transmitted
        spaced with *interval* bit times. The LIN interface will interrupt the
        sequence when a LIN message or another command is received. The stream
        of wakeups will be recived as incoming messages with the
        `MessageFlag.RX` flag.

        Args:
            count (`int`): The number of wakeup frames to send.
            interval (`int`): The time, in bit times, between the wakeup  frames.

        """
        dll.linWriteWakeup(self.handle, count, interval)
