from ..cenum import CEnum, CFlag


class MessageFlag(CFlag):
    """LIN message flags

    The following flags is used in `.LINFrame.flags`.

    """

    TX = 1  #: The message was something we transmitted on the bus.
    RX = 2  #: The message was something we received from the bus.
    WAKEUP_FRAME = 4  # A: wake up frame was received. Id/msg/dlc are undefined.
    NODATA = 8  #: No data, only a header.
    CSUM_ERROR = 16  #: Checksum error
    PARITY_ERROR = 32  #: ID parity error
    SYNC_ERROR = 64  #: A synch error
    SYNCH_ERROR = SYNC_ERROR  #: A synch error
    BIT_ERROR = 128  #: Bit error when transmitting.


class ChannelData(CEnum):
    """linCHANNELDATA_xxx

    These defines are used in `getChannelData`.

    """

    CARD_FIRMWARE_REV = 9  #: Firmware version from the LIN interface.


class ChannelType(CEnum):
    """Flags for `openChannel`"""

    MASTER = 1  #: The LIN interface will be a LIN master
    SLAVE = 2  #: The LIN interface will be a LIN slave


class MessageDisturb(CEnum):
    """LIN illegal message flags"""

    CSUM = 1  #: The checksum of transmitted messages will be inverted
    PARITY = 2  #: The two parity bits will be inverted, used only in master mode.


class MessageParity(CEnum):
    """LIN message parity

    + `MessageParity.STANDARD` == ``LIN_MSG_USE_STANDARD_PARITY``
    + `MessageParity.ENHANCED` == ``LIN_MSG_USE_ENHANCED_PARITY``

    """

    STANDARD = 0x04  #: Use standard (1.x) parity for the specified msg
    ENHANCED = 0x08  #: Use enhanced (2.x) parity for the specified msg


class Setup(CFlag):
    """Used in `Channel.setupLIN`"""

    #: When specified, the LIN interface will use the "enhanced" checksum
    #: according to LIN 2.0.
    #: Note that as per the LIN 2.0 spec) the enhanced
    #: checksum is not used on the diagnostic frames even if the
    #: `Setup.ENHANCED_CHECKSUM` setting is in effect.
    ENHANCED_CHECKSUM = 1

    #: When specified, turns variable message length on, so the the message
    #: length will depend on the message ID.
    VARIABLE_DLC = 2


class Error(CEnum):
    NOMSG = (-1,)  #: No messages available
    NOTRUNNING = (-3,)  #: Handle not on-bus. Some functions requires that the handle is on-bus before being called.
    RUNNING = (-4,)  #: Handle not off-bus. Some functions requires that the handle is off-bus before being called.
    MASTERONLY = (-5,)  #: The function is only for a master.
    SLAVEONLY = (-6,)  #: The function is only for a slave.
    PARAM = (-7,)  #: Error in parameter
    NOTFOUND = (-8,)  #: Specified hardware not found. This error is reported when the LIN transceiver isn't powered up
    NOMEM = (-9,)  #: Out of memory
    NOCHANNELS = (-10,)  #: No channels avaliable
    TIMEOUT = (-11,)  #: Timeout occurred
    NOTINITIALIZED = (-12,)  #: Library not initialized
    NOHANDLES = (-13,)  #: Can't get handle
    INVHANDLE = (-14,)  #: Handle is invalid
    CANERROR = (-15,)  #: Internal error in the driver
    ERRRESP = (-16,)  #: There was an error response from the LIN interface
    WRONGRESP = (-17,)  #: The LIN interface response wasn't the expected one
    DRIVER = (-18,)  #: CAN driver type not supported
    DRIVERFAILED = (-19,)  #: DeviceIOControl failed
    NOCARD = (-20,)  #: The card was removed or not inserted
    LICENSE = (-21,)  #: The license is not valid
    INTERNAL = (-22,)  #: Internal error in the driver
    NO_ACCESS = (-23,)  #: Access denied
    VERSION = (-24,)  #: Function not supported in this version
    NO_REF_POWER = (-25,)  #: Function not supported in this version
    NOT_IMPLEMENTED = (-26,)  #: The requested feature or function is not implemented in the device you are trying to use it on
