from ..cenum import CEnum, CFlag


class Error(CEnum):
    """canERR_xxx"""
    PARAM = -1  #: Error in one or more parameters.
    NOMSG = -2  #: There were no messages to read.
    NOTFOUND = -3  #: Specified device or channel not found.
    NOMEM = -4  #: Out of memory.
    NOCHANNELS = -5  #: No channels available.
    INTERRUPTED = -6  #: Interrupted by signals.
    TIMEOUT = -7  #: Timeout occurred.
    NOTINITIALIZED = -8  #: The library is not initialized.
    NOHANDLES = -9  #: Out of handles
    INVHANDLE = -10  #: Handle is invalid
    INIFILE = -11  #: Error in the ini-file (16-bit only)
    DRIVER = -12  #: Driver type not supported
    TXBUFOFL = -13  #: Transmit buffer overflow
    HARDWARE = -15  #: A hardware error has occurred
    DYNALOAD = -16  #: A driver DLL can't be found or loaded
    DYNALIB = -17  #: A DLL seems to have wrong version
    DYNAINIT = -18  #: Error when initializing a DLL
    NOT_SUPPORTED = -19  #: Operation not supported by hardware or firmware
    RESERVED_5 = -20  #: Reserved
    RESERVED_6 = -21  #: Reserved
    RESERVED_2 = -22  #: Reserved
    DRIVERLOAD = -23  #: Can't find or load kernel driver
    DRIVERFAILED = -24  #: DeviceIOControl failed, use Win32 GetLastError() to learn more
    NOCONFIGMGR = -25  #: Can't find req'd config s/w (e.g. CS/SS)
    NOCARD = -26  #: The card was removed or not inserted
    RESERVED_7 = -27  #: Reserved
    REGISTRY = -28  #: Error (missing data) in the Registry
    LICENSE = -29  #: The license is not valid.
    INTERNAL = -30  #: Internal error in the driver.
    NO_ACCESS = -31  #: Access denied.
    NOT_IMPLEMENTED = -32  #: Not implemented.
    DEVICE_FILE = -33  #: Device File error.
    HOST_FILE = -34  #: Host File error.
    DISK = -35  #: Disk error.
    CRC = -36  #: CRC error.
    CONFIG = -37  #: Configuration Error.
    MEMO_FAIL = -38  #: Memo Error.
    SCRIPT_FAIL = -39  #: Script Fail.
    SCRIPT_WRONG_VERSION = -40  #: Unsupported t program version.
    TXE_CONTAINER_VERSION = -41  #: Unsuppoted txe version.
    TXE_CONTAINER_FORMAT = -42  #: Parsing t program failed.
    BUFFER_TOO_SMALL = -43  #: Buffer provided was not large enough.
    IO_WRONG_PIN_TYPE = -44  #: I/O pin doesn't exist or the I/O pin type doesn't match.
    IO_NOT_CONFIRMED = -45  #: The I/O pin configuration is not confirmed.
    IO_CONFIG_CHANGED = -46  #: The I/O pin configuration has changed after last confirmation.
    IO_PENDING = -47  #: The previous I/O pin value has not yet changed the output.
    IO_NO_VALID_CONFIG = -48  #: There is no valid I/O pin configuration.

    # Used in REST API
    INVALID_PASSWORD = -128
    NO_SUCH_FUNCTION = -129
    NOT_AUTHORIZED = -130
    INVALID_SESSION = -131


class Open(CFlag):
    """Flags used in the flags argument to `.canlib.openChannel()`."""

    # canOpen_xxx
    NOFLAG = 0
    EXCLUSIVE = 0x0008  #: Don't allow sharing of this CANlib channel.
    """Don't allow sharing between multiple `.Channel` objects.

    Two or more threads or applications can share the same CAN channel by
    opening the same CANlib channel multiple times. If this is not desired you
    can open a CANlib channel exclusively once by passing the `.EXCLUSIVE`
    flag. If the CANlib channel is aleady open, the call to
    `.canlib.openChannel()` will fail.

    """
    REQUIRE_EXTENDED = 0x0010
    """This flag causes two things to happen:

        #. The call will fail if the specified circuit doesn't allow extended CAN (CAN 2.0B).

        #. If no frame-type flag is specified in a call to `.Channel.write()`, it is assumed that extended CAN should be used.

    """
    ACCEPT_VIRTUAL = 0x0020
    """Allow opening of virtual channels as well as physical channels."""
    OVERRIDE_EXCLUSIVE = 0x0040
    """Open the channel even if it is opened for exclusive access already."""
    REQUIRE_INIT_ACCESS = 0x0080
    """Fail the call if the channel cannot be opened with init access.

    Init access means that the CAN handle can set bit rate and CAN driver
    mode. At most one CAN handle may have init access to any given channel. If
    you try to set the bit rate or CAN driver mode for a handle to which you
    don't have init access, the call will silently fail (i.e. `canOK` is
    returned although the call had no effect), unless you enable "access error
    reporting" by using `.Channel.IOControlItem.SET_REPORT_ACCESS_ERRORS`. Access error
    reporting is by default off. Init access is the default.

    """
    NO_INIT_ACCESS = 0x0100
    """Don't open the handle with init access.

    Note: A handle opened without init access will still set default bitrate
    when going on bus, if no other handle has opened the channel with init
    access at the time of the buson.

    """
    ACCEPT_LARGE_DLC = 0x0200
    """DLC can be greater than 8.

    The channel will accept CAN messages with DLC (Data Length Code) greater
    than 8. If this flag is not used, a message with DLC > 8 will always be
    reported or transmitted as a message with DLC = 8. When the
    `ACCEPT_LARGE_DLC` flag is used, the message will be sent and/or received
    with the true DLC, which can be at most 15. The length of the message is
    always at most 8.

    """
    CAN_FD = 0x0400
    """The channel will use the CAN FD protocol, ISO compliant.

    This also means that messages with `.MessageFlag.FDF`, `.MessageFlag.BRS`
    and `.MessageFlag.ESI` can now be used.

    """
    CAN_FD_NONISO = 0x0800
    """The channel will use the CAN FD NON-ISO protocol.

    Use this if you want to configure the can controller to be able to communicate with
    a can controller designed prior to the release of the CAN FD ISO specification.

    Non ISO mode implies:

        #. The stuff bit counter will not be included in the frame format.
        #. Initial value for CRC17 and CRC21 will be zero.

    This also means that messages with `.MessageFlag.FDF`, `.MessageFlag.BRS`
    and `.MessageFlag.ESI` can now be used.

    """


class IOControlItem(CEnum):
    """An enumeration used in `.Channel.iocontrol`."""
    PREFER_EXT = 1  #: Tells CANlib to "prefer" extended identifiers.
    PREFER_STD = 2  #: Tells CANlib to "prefer" standard identifiers.
    CLEAR_ERROR_COUNTERS = 5  #: Clear the CAN error counters.
    SET_TIMER_SCALE = 6  #: Set time-stamp clock resolution in microseconds, default 1000.
    SET_TXACK = 7  #: Enable/disable Transmit Acknowledge.
    GET_RX_BUFFER_LEVEL = 8  #: Current receive queue, RX, level.
    GET_TX_BUFFER_LEVEL = 9  #: Current transmitt queue, TX, level.
    FLUSH_RX_BUFFER = 10  #: Discard contents of the RX queue.
    FLUSH_TX_BUFFER = 11  #: Discard contents of the TX queue.
    GET_TIMER_SCALE = 12  #: Current time-stamp clock resolution in microseconds.
    SET_TXRQ = 13  #: Turn transmit requests on or off.
    GET_EVENTHANDLE = 14  #: Windows only.
    SET_BYPASS_MODE = 15  #: Not implemented.
    SET_WAKEUP = 16  #: For internal use only.
    GET_DRIVERHANDLE = 17  #: Windows only.
    MAP_RXQUEUE = 18  #: For internal use only.
    GET_WAKEUP = 19  #: For internal use only.
    SET_REPORT_ACCESS_ERRORS = 20  #: Turn access error reporting on/off.
    GET_REPORT_ACCESS_ERRORS = 21  #: Current setting of access error reporting
    CONNECT_TO_VIRTUAL_BUS = 22  #: Windows only
    DISCONNECT_FROM_VIRTUAL_BUS = 23  #: Windows only
    SET_USER_IOPORT = 24  #: Set IO port to value.
    GET_USER_IOPORT = 25  #: Read IO port value.
    SET_BUFFER_WRAPAROUND_MODE = 26  #: For internal use only.
    SET_RX_QUEUE_SIZE = 27  #: Windows only.
    SET_USB_THROTTLE = 28  #: For internal use only.
    GET_USB_THROTTLE = 29  #: For internal use only.
    SET_BUSON_TIME_AUTO_RESET = 30  #: Enable/disable time reset at bus on.
    GET_TXACK = 31  #: Status of Transmit Acknowledge.
    SET_LOCAL_TXECHO = 32  #: Turn on/off local transmit echo.
    SET_ERROR_FRAMES_REPORTING = 33  #: Windows only
    GET_CHANNEL_QUALITY = 34  #: Read remote channel quality.
    GET_ROUNDTRIP_TIME = 35  #: Round trip time in ms, for remote channel.
    GET_BUS_TYPE = 36  #: Windows only.
    GET_DEVNAME_ASCII = 37  #: Retreive device name.
    GET_TIME_SINCE_LAST_SEEN = 38  #: For WLAN devices, this is the time since the last keep-alive message.
    GET_TREF_LIST = 39  #: Unsupported
    TX_INTERVAL = 40  #: Minimum CAN message transmit interval
    SET_THROTTLE_SCALED = 41  #: Windows only
    GET_THROTTLE_SCALED = 42  #: Windows only
    SET_BRLIMIT = 43  #: Max bitrate limit can be overridden with this IOCTL.
    RESET_OVERRUN_COUNT = 44  #: Reset overrun count and flags.
    LIN_MODE = 45  #: For internal use only.
    SET_LOCAL_TXACK = 46  #: Enable reception of canMSG_LOCAL_TXACK.


# In the returned type, document the function call to use
class ChannelDataItem(CEnum):
    """Low level helper object representing ``canCHANNELDATA_xxx``.

    See the properties of `ChannelData` for how to get retrieve this data.

    """
    CHANNEL_CAP = 1  #: capabilities of the CAN controller, see `ChannelData.channel_cap`
    TRANS_CAP = 2  #: capabilities of the CAN transceiver, see `ChannelData.trans_cap`
    CHANNEL_FLAGS = 3  #: status of the channel as flags, see `ChannelData.channel_flags`
    CARD_TYPE = 4  #: hardware type of the card, see `ChannelData.card_type`
    CARD_NUMBER = 5  #: the card's number in the computer, see `ChannelData.card_number`
    CHAN_NO_ON_CARD = 6  #: local channel number on the card, see `ChannelData.chan_no_on_card`
    CARD_SERIAL_NO = 7  #: serial number of the card, or 0, see `ChannelData.card_serial_no`
    TRANS_SERIAL_NO = 8  #: serial number of the transceiver, or 0, see `ChannelData.trans_serial_no`
    CARD_FIRMWARE_REV = 9  #: firmware revision number on the card, see `ChannelData.card_firmware_rev`
    CARD_HARDWARE_REV = 10  #: version of the card's hardware, see `ChannelData.card_hardware_rev`
    CARD_UPC_NO = 11  #: EAN of the card, see `ChannelData.card_upc_no`
    TRANS_UPC_NO = 12  #: EAN of the transceiver, see `ChannelData.trans_upc_no`
    CHANNEL_NAME = 13  #: Deprecated
    DLL_FILE_VERSION = 14  #: version of the dll file, see `ChannelData.dll_file_version`
    DLL_PRODUCT_VERSION = 15  #: version of the CANlib, see `ChannelData.dll_product_version`
    DLL_FILETYPE = 16  #: see `ChannelData.dll_filetype`
    TRANS_TYPE = 17  #: transceiver type, see `ChannelData.trans_type`
    DEVICE_PHYSICAL_POSITION = 18  #: see `ChannelData.device_physical_position`
    UI_NUMBER = 19  #: see `ChannelData.ui_number`
    TIMESYNC_ENABLED = 20  #: see `ChannelData.timesync_enabled`
    DRIVER_FILE_VERSION = 21  #: version of the driver, see `ChannelData.driver_file_version`
    DRIVER_PRODUCT_VERSION = 22  #: version of the CANlib, see `ChannelData.driver_product_version`
    MFGNAME_UNICODE = 23  #: manufacturer's name, see `ChannelData.mfgname_unicode`
    MFGNAME_ASCII = 24  #: manufacturer's name, see `ChannelData.mfgname_ascii`
    DEVDESCR_UNICODE = 25  #: product name of the device, see `ChannelData.devdescr_unicode`
    DEVDESCR_ASCII = 26  #: product name of the device, see `ChannelData.devdescr_ascii`
    DRIVER_NAME = 27  #: device driver name, see `ChannelData.driver_name`
    CHANNEL_QUALITY = 28  #: see `ChannelData.channel_quality`
    ROUNDTRIP_TIME = 29  #: see `ChannelData.roundtrip_time`
    BUS_TYPE = 30  #: see `ChannelData.bus_type`
    DEVNAME_ASCII = 31  #: see `ChannelData.devname_ascii`
    TIME_SINCE_LAST_SEEN = 32  #: see `ChannelData.time_since_last_seen`
    REMOTE_OPERATIONAL_MODE = 33  #: see `ChannelData.remote_operational_mode`
    REMOTE_PROFILE_NAME = 34  #: see `ChannelData.remote_profile_name`
    REMOTE_HOST_NAME = 35  #: see `ChannelData.remote_host_name`
    REMOTE_MAC = 36  #: see `ChannelData.remote_mac`
    MAX_BITRATE = 37  #: see `ChannelData.max_bitrate`
    CHANNEL_CAP_MASK = 38  #: see `ChannelData.channel_cap_mask`
    CUST_CHANNEL_NAME = 39  #: see `ChannelData.cust_channel_name`
    IS_REMOTE = 40  #: see `ChannelData.is_remote`
    REMOTE_TYPE = 41  #: see `ChannelData.remote_type`
    LOGGER_TYPE = 42  #: see `ChannelData.logger_type`
    HW_STATUS = 43  #: see `ChannelData.hw_status`
    FEATURE_EAN = 44  #: see `ChannelData.feature_ean`
    BUS_PARAM_LIMITS = 45  # Not yet wrapped, BLA-2949
    CLOCK_INFO = 46  #: see `ChannelData.clock_info`
    CHANNEL_CAP_EX = 47  #: see `ChannelData.channel_cap_ex`


class Stat(CFlag):
    """canSTAT_xxx

    The following circuit status flags are returned by `Channel.readStatus`.
    Note that more than one flag might be set at any one time.

    Note:

        Usually both canSTAT_HW_OVERRUN and canSTAT_SW_OVERRUN are set when
        overrun has occurred. This is because the kernel driver can't see the
        difference between a software overrun and a hardware overrun, but the
        code should always test for both types of overruns.

    """

    ERROR_PASSIVE = 0x00000001  #: The circuit is error passive
    BUS_OFF = 0x00000002  #: The circuit is Off Bus
    ERROR_WARNING = 0x00000004  #: At least one error counter > 96
    ERROR_ACTIVE = 0x00000008  #: The circuit is error active.
    TX_PENDING = 0x00000010  #: There are messages pending transmission
    RX_PENDING = 0x00000020  #: There are messages in the receive buffer
    RESERVED_1 = 0x00000040
    TXERR = 0x00000080  #: There has been at least one TX error
    RXERR = 0x00000100  #: There has been at least one RX error of some sort
    HW_OVERRUN = 0x00000200  #: There has been at least one HW buffer overflow
    SW_OVERRUN = 0x00000400  #: There has been at least one SW buffer overflow
    OVERRUN = HW_OVERRUN | SW_OVERRUN  #: Both `HW_OVERRUN` and `SW_OVERRUN` is active


class MessageFlag(CFlag):
    """Message information flags

    The following flags can be returned from `Channel.read` et al, or passed to
    `Channel.write`.

    This enum is a combination of flags for messages, CAN FD messages, and
    message errors. Normal messages flags are the flags covered by `MSG_MASK`,
    CAN FD message flags are those covered by `FDMSG_MASK`, and message errors
    are those covered by `MSGERR_MASK`.

    Note:
        `FDF`, `BRS`, and `ESI` require CAN FD.

        `RTR` cannot be set for CAN FD messages.

        Not all hardware platforms can detect the difference between hardware
        overruns and software overruns, so your application should test for
        both conditions.

    """

    # canMSG_xxx
    MSG_MASK = 0x00FF  #: Used to mask the non-info bits.
    RTR = 0x0001  #: Message is a remote request.
    STD = 0x0002  #: Message has a standard (11-bit) identifier.
    EXT = 0x0004  #: Message has an extended (29-bit) identifier.
    WAKEUP = 0x0008  #: Message is a WAKEUP message, Single Wire CAN.
    NERR = 0x0010  #: NERR was active during the message (TJA1054 hardware)
    ERROR_FRAME = 0x0020  #: Message represents an error frame.
    TXACK = 0x0040  #: Message is a TX ACK (msg has really been sent)
    TXRQ = 0x0080  #: Message is a TX REQUEST (msg was transfered to the chip)
    LOCAL_TXACK = 0x10000000  #: Message is a LOCAL TX ACK (was transmitted from another handle on the same channel)

    #
    SINGLE_SHOT = 0x1000000  #: Message is Single Shot, try to send once, no retransmission.
    TXNACK = 0x2000000  #: Message is a failed Single Shot, message was not sent.
    ABL = 0x4000000  #: Single shot message was not sent because arbitration was lost.

    # canFDMSG_xxx
    FDMSG_MASK = 0xFF0000  #: obsolete
    FDF = 0x010000  #: Message is a CAN FD message.
    EDL = FDF  #: obsolete
    BRS = 0x020000  #: Message is sent/received with bit rate switch (CAN FD)
    ESI = 0x040000  #: Sender of the message is in error passive mode (CAN FD)

    # canMSGERR_xxx
    MSGERR_MASK = 0xFF00  #: Used to mask the non-error bits
    HW_OVERRUN = 0x0200  #: Hardware buffer overrun.
    SW_OVERRUN = 0x0400  #: Software buffer overrun.
    STUFF = 0x0800  #: Stuff error.
    FORM = 0x1000  #: Form error.
    CRC = 0x2000  #: CRC error.
    BIT0 = 0x4000  #: Sent dominant bit, read recessive bit
    BIT1 = 0x8000  #: Sent recessive bit, read dominmant bit
    OVERRUN = HW_OVERRUN | SW_OVERRUN  #: Both SW and HW overrun conditions
    BIT = 0xC000  #: All bit error.
    BUSERR = 0xF800  #: All RX error.

    def __contains__(self, item):
        # The correct test for overrun would be:
        #   if Stat.HW_OVERRUN in frame.flags or Stat.SW_OVERRUN in frame.flags
        # But the user will probably just write:
        #   if Stat.OVERRUN in frame.flags
        # So let us help the user if the check is against the OVERRUN flag
        if item == self.OVERRUN:
            return self & self.HW_OVERRUN or self & self.SW_OVERRUN
        else:
            return self & item


class Driver(CEnum):
    NORMAL = 4  #: The "normal" driver type (push-pull). This is the default.
    SILENT = 1  #: Sets the CAN controller in Silent Mode.
    SELFRECEPTION = 8  #: Self-reception. Not implemented.
    OFF = 0  #: The driver is turned off. Not implemented in all types of hardware.


class ScriptStatus(CFlag):
    """Status of t program

    .. versionadded:: 1.6

    .. versionchanged:: 1.7
       Is now based on `IntFlag` instead of `IntEnum`

    """

    IDLE = 0
    LOADED = 1
    RUNNING = 2


class ScriptStop(CEnum):
    NORMAL = 0
    FORCED = -9


class TxeDataItem(CEnum):
    FILE_VERSION = 1  #: The three part version number of the compiled script file (.txe) file format.
    COMPILER_VERSION = 2  #: The three part version number of the compiler used to create the compiled script file (.txe).
    DATE = 3
    """Compilation date in Coordinated Universal Time (UTC) of the compiled script file (.txe).

    Contents: 0. Year, 1. Month, 2. Day, 3. Hour, 4. Minute, 5. Second.

    """
    DESCRIPTION = 4  #: Description of the compiled script file (.txe).
    SOURCE = 5  #: The name followed by the content of each unencrypted source file
    SIZE_OF_CODE = 6  #: The size of the compiled code in the .txe file.
    IS_ENCRYPTED = 7  #: Non-zero value if the compiled script file (.txe) contents is encrypted.


class DeviceMode(CEnum):
    """kvDEVICE_MODE_xxx"""
    INTERFACE = 0  #: Device is running or should be running in interface mode.
    LOGGER = 1  #: Device is running or should be running in logger mode.


class EnvVarType(CEnum):
    """kvENVVAR_TYPE_xxx"""
    INT = 1  #: The type of the envvar is C ``int``.
    FLOAT = 2  #: The type of the envvar is C ``float``.
    STRING = 3  #: The type of the envvar is C ``string``.


class AcceptFilterFlag(CEnum):
    """canFILTER_SET_xxx"""

    # Flags for canAccept().
    SET_CODE_STD = 3
    SET_MASK_STD = 4
    SET_CODE_EXT = 5
    SET_MASK_EXT = 6
    NULL_MASK = 0


class Bitrate(CEnum):
    """canBITRATE_xxx

    Predefined CAN bitrates.
    See `BitrateFD` for predefined CAN FD bitrates.

    .. versionadded:: 1.17

    """

    BITRATE_1M = -1  #: Indicate a bitrate of 1 Mbit/s.
    BITRATE_500K = -2  #: Indicate a bitrate of 500 kbit/s.
    BITRATE_250K = -3  #: Indicate a bitrate of 250 kbit/s.
    BITRATE_125K = -4  #: Indicate a bitrate of 125 kbit/s.
    BITRATE_100K = -5  #: Indicate a bitrate of 100 kbit/s.
    BITRATE_62K = -6  #: Indicate a bitrate of 62 kbit/s.
    BITRATE_50K = -7  #: Indicate a bitrate of 50 kbit/s.
    BITRATE_83K = -8  #: Indicate a bitrate of 83 kbit/s.
    BITRATE_10K = -9  #: Indicate a bitrate of 10 kbit/s.


class BitrateFD(CEnum):
    """canFD_BITRATE_xxx

    Predefined CAN FD bitrates.  Used when setting bitrates using the CAN FD
    protocol, see `Bitrate` for predefined CAN bitrates.

    .. versionadded:: 1.17

    """

    BITRATE_500K_80P = -1000  #: Indicates a bitrate of 500 kbit/s and sampling point at 80%.
    BITRATE_1M_80P = -1001  #: Indicates a bitrate of 1 Mbit/s and sampling point at 80%.
    BITRATE_2M_80P = -1002  #: Indicates a bitrate of 2 Mbit/s and sampling point at 80%.
    BITRATE_2M_60P = -1007  #: Indicates a bitrate of 2 Mbit/s and sampling point at 60%.
    BITRATE_4M_80P = -1003  #: Indicates a bitrate of 4 Mbit/s and sampling point at 80%.
    BITRATE_8M_60P = -1004  #: Indicates a bitrate of 8 Mbit/s and sampling point at 60%.
    BITRATE_8M_70P = -1006  #: Indicates a bitrate of 8 Mbit/s and sampling point at 70%.
    BITRATE_8M_80P = -1005  #: Indicates a bitrate of 8 Mbit/s and sampling point at 80%.


class LEDAction(CEnum):
    """kvLED_ACTION_xxx

    The following can be used together with `canlib.canlib.Channel.flashLeds`.

    .. versionchanged:: 1.18
       Added LEDs 4 through 11 (needs CANlib v5.19+)

    """

    ALL_LEDS_ON = 0  #: Turn all LEDs on.
    ALL_LEDS_OFF = 1  #: Turn all LEDs off.
    LED_0_ON = 2  #: Turn LED 0 on.
    LED_0_OFF = 3  #: Turn LED 0 off.
    LED_1_ON = 4  #: Turn LED 1 on.
    LED_1_OFF = 5  #: Turn LED 1 off.
    LED_2_ON = 6  #: Turn LED 2 on.
    LED_2_OFF = 7  #: Turn LED 2 off.
    LED_3_ON = 8  #: Turn LED 3 on.
    LED_3_OFF = 9  #: Turn LED 3 off.
    LED_4_ON = 10  #: Turn LED 4 on.
    LED_4_OFF = 11  #: Turn LED 4 off.
    LED_5_ON = 12  #: Turn LED 5 on.
    LED_5_OFF = 13  #: Turn LED 5 off.
    LED_6_ON = 14  #: Turn LED 6 on.
    LED_6_OFF = 15  #: Turn LED 6 off.
    LED_7_ON = 16  #: Turn LED 7 on.
    LED_7_OFF = 17  #: Turn LED 7 off.
    LED_8_ON = 18  #: Turn LED 8 on.
    LED_8_OFF = 19  #: Turn LED 8 off.
    LED_9_ON = 20  #: Turn LED 9 on.
    LED_9_OFF = 21  #: Turn LED 9 off.
    LED_10_ON = 22  #: Turn LED 10 on.
    LED_10_OFF = 23  #: Turn LED 10 off.
    LED_11_ON = 24  #: Turn LED 11 on.
    LED_11_OFF = 25  #: Turn LED 11 off.


class TransceiverType(CEnum):
    """Transceiver (logical) types

    The following constants can be returned from canGetChannelData(), using the
    canCHANNELDATA_TRANS_TYPE item code. They identify the bus transceiver type
    for the channel specified in the call to canGetChannelData.

    Note:

        If the type starts with a number ``T_`` has been prepended to the name.

        They indicate a hardware type, but not necessarily a specific circuit
        or product.

    """

    UNKNOWN = 0  #: Unknown or undefined
    T_251 = 1  #: 82c251
    T_252 = 2  #: 82c252, TJA1053, TJA1054
    DNOPTO = 3  #: Optoisolated 82C251
    W210 = 4
    SWC_PROTO = 5  #: AU5790 prototype
    SWC = 6  #: AU5790
    EVA = 7
    FIBER = 8  #: 82c251 with fibre extension
    K251 = 9  #: K-line + 82c251
    K = 10  #: K-line, without CAN.
    T_1054_OPTO = 11  #: TJA1054 with optical isolation
    SWC_OPTO = 12  #: AU5790 with optical isolation
    TT = 13  #: B10011S Truck-And-Trailer
    T_1050 = 14  #: TJA1050
    T_1050_OPTO = 15  #: TJA1050 with optical isolation
    T_1041 = 16  #: TJA1041
    T_1041_OPTO = 17  #: TJA1041 with optical isolation
    RS485 = 18  #: RS485 (i.e. J1708)
    LIN = 19
    KONE = 20
    CANFD = 22
    CANFD_LIN = 24  #: HYBRID CAN-FD/LIN
    CANFD_SIC = 26  #: CAN-FD SIC transceiver
    LINX_LIN = 64
    LINX_J1708 = 66
    LINX_K = 68
    LINX_SWC = 70
    LINX_LS = 72


class Notify(CFlag):
    """canNOTIFY_xxx

    These notify flags are used in `Channel.set_callback` to indicate
    different kind of events.

    """

    NONE = 0  #: Turn notifications off.
    RX = 0x0001  #: CAN message reception notification
    TX = 0x0002  #: CAN message transmission notification
    ERROR = 0x0004  #: CAN bus error notification
    STATUS = 0x0008  #: CAN chip status change
    ENVVAR = 0x0010  #: An environment variable was changed by a script. Note that you will not be notified when an environment variable is updated from the Canlib API.
    BUSONOFF = 0x0020  #: Notify on bus on/off status changed
    REMOVED = 0x0040  #: Notify on device removed


class ChannelFlags(CFlag):
    """canCHANNEL_IS_xxx

    These channel flags are used in conjunction with `ChannelDataItem.channel_flags`.

    """

    IS_EXCLUSIVE = 0x0001  #: Channel is opened exclusively.
    IS_OPEN = 0x0002  #: Channel is active, either opened in LIN mode or on-bus in CAN mode.
    IS_CANFD = 0x0004  #: Channel has been opened as CAN FD.
    IS_LIN = 0x0010  #: Channel has been opened as LIN.
    IS_LIN_MASTER = 0x0020  #: Channel has been opened as a LIN master.
    IS_LIN_SLAVE = 0x0040  #: Channel has been opened as a LIN slave.


class BusTypeGroup(CEnum):
    """kvBUSTYPE_GROUP_xxx

    Bus type group. This is a grouping of the individual kvBUSTYPE_xxx.

    """

    VIRTUAL = 1
    LOCAL = 2  #: kvBUSTYPE_USB
    REMOTE = 3  #: kvBUSTYPE_WLAN, kvBUSTYPE_LAN
    INTERNAL = 4  #: kvBUSTYPE_PCI, kvBUSTYPE_PCMCIA, ...


class HardwareType(CEnum):
    """canHWTYPE_xxx

    The following constants can be returned from `ChannelData`, using the
    `card_type` property. They identify the hardware type for the current
    channel.

    Note:

        The members indicate a hardware type, but not necessarily a specific
        product. For example, `canHWTYPE_LAPCAN` is returned both for LAPcan
        and LAPcan II. (Use the `card_upc_no` property of `ChannelData` to
        obtain the UPC/EAN code for the device. This number uniquely identifies
        the product.)

    """

    NONE = 0  #: Unknown or undefined.
    VIRTUAL = 1  #: The virtual CAN bus.
    LAPCAN = 2  #: LAPcan Family.
    PCCAN = 8  #: PCcan Family.
    PCICAN = 9  #: PCIcan Family.
    PCICAN_II = 40  #: PCIcan II family.
    USBCAN_II = 42  #: USBcan II, USBcan Rugged, Kvaser Memorator.
    LEAF = 48  #: Kvaser Leaf Family.
    PC104_PLUS = 50  #: Kvaser PC104+.
    PCICANX_II = 52  #: Kvaser PCIcanx II.
    MEMORATOR_II = 54  #: Kvaser Memorator Professional family.
    MEMORATOR_PRO = 54  #: Kvaser Memorator Professional family.
    USBCAN_PRO = 56  #: Kvaser USBcan Professional.
    BLACKBIRD = 58  #: Kvaser BlackBird.
    MEMORATOR_LIGHT = 60  #: Kvaser Memorator Light.
    EAGLE = 62  #: Kvaser Eagle family.
    BLACKBIRD_V2 = 64  #: Kvaser BlackBird v2.
    MINIPCIE = 66  #: Kvaser Mini PCI Express.
    USBCAN_KLINE = 68  #: USBcan Pro HS/K-Line.
    ETHERCAN = 70  #: Kvaser Ethercan.
    USBCAN_LIGHT = 72  #: Kvaser USBcan Light.
    USBCAN_PRO2 = 74  #: Kvaser USBcan Pro 5xHS and variants.
    PCIE_V2 = 76  #: Kvaser PCIEcan 4xHS and variants.
    MEMORATOR_PRO2 = 78  #: Kvaser Memorator Pro 5xHS and variants.
    LEAF2 = 80  #: Kvaser Leaf Pro HS v2 and variants.
    MEMORATOR_V2 = 82  #: Kvaser Memorator (2nd generation).
    CANLINHYBRID = 84  #: Kvaser Hybrid CAN/LIN.
    DINRAIL = 86  #: Kvaser DIN Rail SE400S and variants.
    U100 = 88  #: Kvaser U100 and variants.
    LEAF_V3 = 90 #: Kvaser Kvaser Leaf v3 and variants.

    # Obsolete
    CANPARI = 3  #: CANpari (obsolete).
    USBCAN = 11  #: USBcan (obsolete).
    SIMULATED = 44  #: Simulated CAN bus for Kvaser Creator (obsolete).
    ACQUISITOR = 46  #: Kvaser Acquisitor (obsolete).
    IRIS = 58  #: Obsolete name, use `BLACKBIRD` instead.
    MINIHYDRA = 62  #: Obsolete name, use `EAGLE` instead.
    BAGEL = 64  #: Obsolete name, use `BLACKBIRD_V2` instead.


class ChannelCap(CFlag):
    """canCHANNEL_CAP_xxx

    Channel capabilities.

    .. versionchanged:: 1.8

    """

    EXTENDED_CAN = 0x00000001  #: Can use extended identifiers.
    BUS_STATISTICS = 0x00000002  #: Can report busload etc.
    ERROR_COUNTERS = 0x00000004  #: Can return error counters.
    RESERVED_2 = 0x00000008  #: Obsolete, only used by LAPcan driver
    GENERATE_ERROR = 0x00000010  #: Can send error frames.
    GENERATE_OVERLOAD = 0x00000020  #: Can send CAN overload frame.
    TXREQUEST = 0x00000040  #: Can report when a CAN messsage transmission is initiated.
    TXACKNOWLEDGE = 0x00000080  #: Can report when a CAN messages has been transmitted.
    VIRTUAL = 0x00010000  #: Virtual CAN channel.
    SIMULATED = 0x00020000  #: Simulated CAN channel.
    RESERVED_1 = (
        0x00040000  # Obsolete, use `canCHANNEL_CAP_REMOTE_ACCESS` or `.Channel.canGetChannelData()` instead.
    )
    CAN_FD = 0x00080000  #: CAN-FD ISO compliant channel.
    CAN_FD_NONISO = 0x00100000  #: CAN-FD NON-ISO compliant channel.
    SILENT_MODE = 0x00200000  #: Channel supports Silent mode.
    SINGLE_SHOT = 0x00400000  #: Channel supports Single Shot messages.
    LOGGER = 0x00800000  #: Channel has logger capabilities.
    REMOTE_ACCESS = 0x01000000  #: Channel has remote capabilities.
    SCRIPT = 0x02000000  #: Channel has script capabilities.
    LIN_HYBRID = 0x04000000  #: Channel has LIN capabilities.
    IO_API = 0x08000000  #: Channel has diagnostic capabilities.
    DIAGNOSTICS = 0x10000000  #: Channel has diagnostic capabilities.


class ChannelCapEx(CFlag):
    """canCHANNEL_CAP_EX_xxx

    Channel extended capabilities.

    .. versionadded:: 1.17

    """

    BUSPARAMS_TQ = 0x0000000000000001  # Channel has BusParams TQ API.


class LoggerType(CEnum):
    """kvLOGGER_TYPE_xxx

    Logger type, returned when using `ChannelData.logger_type`.

    """

    NOT_A_LOGGER = 0
    V1 = 1
    V2 = 2


class OperationalMode(CEnum):
    """canCHANNEL_OPMODE_xxx

    Current WLAN operational mode.

    """

    NONE = 1  #: Not applicable, or unknown mode.
    INFRASTRUCTURE = 2  #: Infrastructure mode
    RESERVED = 3  #: Reserved
    ADH = 4  #: Adhoc mode


class RemoteType(CEnum):
    """kvREMOTE_TYPExxx

    Remote type, returned when using canCHANNELDATA_REMOTE_TYPE
    """

    NOT_REMOTE = 0
    WLAN = 1
    LAN = 2


class DriverCap(CEnum):
    """canDRIVER_CAP_xxx

    Driver (transceiver) capabilities.
    """

    HIGHSPEED = 0x00000001


class ScriptRequest(CEnum):
    """kvSCRIPT_REQUEST_TEXT_xxx

    These defines are used in kvScriptRequestText() for printf message
    subscribe/unsubscribe.

    """

    UNSUBSCRIBE = 1
    SUBSCRIBE = 2
    ALL_SLOTS = 255


class VersionEx(CEnum):
    VERSION = 0
    PRODVER = 1
    PRODVER32 = 2
    BETA = 3
