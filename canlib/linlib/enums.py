from ..cenum import CEnum, CFlag


class MessageFlag(CFlag):
    """LIN message flags

    The following flags is used in `canlib.LINFrame.flags`.

    """

    TX = 1  # The message was something we transmitted on the bus.
    RX = 2  # The message was something we received from the bus.
    WAKEUP_FRAME = 4  # A wake up frame was received. Id/msg/dlc are undefined.
    NODATA = 8  # No data, only a header.
    CSUM_ERROR = 16
    PARITY_ERROR = 32
    SYNC_ERROR = 64
    SYNCH_ERROR = SYNC_ERROR
    BIT_ERROR = 128  # Bit error when transmitting.


class ChannelData(CEnum):
    """linCHANNELDATA_xxx

    These defines are used in `getChannelData`.

    """

    CARD_FIRMWARE_REV = 9


class ChannelType(CEnum):
    """Flags for `openChannel`"""

    MASTER = 1
    SLAVE = 2


class MessageDisturb(CEnum):
    """LIN illegal message flags"""

    CSUM = 1
    PARITY = 2


class MessageParity(CEnum):
    """LIN message parity

    + `MessageParity.STANDARD` == ``LIN_MSG_USE_STANDARD_PARITY``
    + `MessageParity.ENHANCED` == ``LIN_MSG_USE_ENHANCED_PARITY``

    """

    STANDARD = 0x04
    ENHANCED = 0x08


class Setup(CFlag):
    """Used in `Channel.setupLIN`"""

    ENHANCED_CHECKSUM = 1
    VARIABLE_DLC = 2


class Error(CEnum):
    NOMSG = (-1,)
    NOTRUNNING = (-3,)
    RUNNING = (-4,)
    MASTERONLY = (-5,)
    SLAVEONLY = (-6,)
    PARAM = (-7,)
    NOTFOUND = (-8,)
    NOMEM = (-9,)
    NOCHANNELS = (-10,)
    TIMEOUT = (-11,)
    NOTINITIALIZED = (-12,)
    NOHANDLES = (-13,)
    INVHANDLE = (-14,)
    CANERROR = (-15,)
    ERRRESP = (-16,)
    WRONGRESP = (-17,)
    DRIVER = (-18,)
    DRIVERFAILED = (-19,)
    NOCARD = (-20,)
    LICENSE = (-21,)
    INTERNAL = (-22,)
    NO_ACCESS = (-23,)
    VERSION = (-24,)
    NO_REF_POWER = (-25,)
    NOT_IMPLEMENTED = (-26,)
