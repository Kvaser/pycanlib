import ctypes as ct
import struct
from collections import namedtuple

from .. import VersionNumber, canlib, dllLoader
from ..ean import EAN
from .dll import LINLibDll
from .enums import ChannelData

_ct_dll = dllLoader.load_dll(win_name='linlib.dll', linux_name='liblinlib.so')
dll = LINLibDll(_ct_dll)
dll.linInitializeLibrary()


TransceiverData = namedtuple('TransceiverData', 'ean serial type')


def getChannelData(channel_number, item=ChannelData.CARD_FIRMWARE_REV):
    """This function can be used to retrieve certain pieces of information about a channel.

    Note:
        You must pass a channel number and not a channel handle.

    Args:

        channel (int): The number of the channel you are interested in. Channel
            numbers are integers in the interval beginning at 0.

        item (`.ChannelData`): This parameter specifies what data to obtain
            for the specified channel. Currently the only item available is
            `~ChannelData.CARD_FIRMWARE_REV`, which is the default.



    """
    if item != ChannelData.CARD_FIRMWARE_REV:
        raise NotImplementedError("linlib.getChannelData only supports getting CARD_FIRMWARE_REV")
    # buffer points to a 64-bit (8 bytes) area which receives the firmware
    # revision number on the card. This number consists of four 16-bit words:
    # the major revision, the minor revision, the release number and the build
    # number, listed in order from the most significant to the least
    # significant. qqqdaca
    buff = ct.create_string_buffer(8)
    dll.linGetChannelData(
        channel_number,
        item,
        ct.byref(buff),
        ct.sizeof(buff),
    )
    # Based on a similar function in the CANlib wrapper, the version number is
    # unpacked with native byte order
    build, release, minor, major = struct.unpack('HHHH', buff.raw)
    # We ignore the release number, because it's not used in canlib and ignored
    # in the Device Guide
    return VersionNumber(major, minor, build)


def getTransceiverData(channel_number):
    """Get the transceiver information for a CAN channel

    The application typically uses this call to find out whether a particular
    CAN channel has a LIN interface connected to it. For a Kvaser LIN Leaf it
    retrieves the transceiver type and device information.

    This function call will open the CAN channel, but no CAN messages are
    transmitted on it. In other words, it's risk-free to use even if no LIN
    interface is connected, or if the channel is connected to a CAN system.

    Note:

        Attempts to use the channel for LIN communication will be meaningful
        only if the returned `TransceiverData`'s ~type~ attribute is one of
        `.TransceiverType.LIN` or `.TransceiverType.CANFD_LIN`

        A LIN interface need not be powered for this call to succeed.

        The information may not always be accurate. Especially after changing
        transceiver on a running LAPcan card, you should go on bus and off bus
        again to be sure the transceiver information is updated.

    """
    ean = ct.create_string_buffer(8)
    serial = ct.create_string_buffer(8)
    ttype = ct.c_int()
    dll.linGetTransceiverData(channel_number, ean, serial, ct.byref(ttype))

    ean = EAN.from_bcd(ean.raw)
    try:
        serial = int.from_bytes(serial.raw, byteorder='little')
    except AttributeError:
        # Python 2 doesn't have int.from_bytes
        serial = int(serial.raw.encode('hex'), 16)
    ttype = canlib.TransceiverType(ttype.value)
    return TransceiverData(ean=ean, serial=serial, type=ttype)


def initializeLibrary():
    """Initialize LINlib

    Note:

        LINlib is automatically initialized when `canlib.linlib` is
        imported. This function is only necessary when LINlib has been manually
        unloaded with `unloadLibrary`.

    """
    dll.linInitializeLibrary()


def unloadLibrary():
    """Deinitialize LINlib

    This function de-initializes the LIN library. After this function is called
    `linInitializeLibrary` must be called before any other LIN function is
    called.

    """
    dll.linUnloadLibrary()


def dllversion():
    """Retrieve the LIN library version as a `~canlib.VersionNumber`

    Note:
        Requires CANlib v5.3
    """
    major = ct.c_int()
    minor = ct.c_int()
    build = ct.c_int()
    dll.linGetVersion(ct.byref(major), ct.byref(minor), ct.byref(build))
    return VersionNumber(major.value, minor.value, build.value)
