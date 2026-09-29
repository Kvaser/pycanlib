from ..cenum import CEnum


class Error(CEnum):
    OK = 0  #: OK!
    FAIL = -1  #: Generic error.
    PARAM = -3  #: Error in supplied parameters.
    LOGFILEOPEN = -8  #: Can't find/open log file.
    NOSTARTTIME = -9  #: Start time not found.
    NOLOGMSG = -10  #: No log message found.
    LOGFILEWRITE = -11  #: Error writing log file.
    EOF = -12  #: End of file found.
    NO_DISK = -13  #: No disk found.
    LOGFILEREAD = -14  #: Error while reading log file.
    QUEUE_FULL = -20  #: Queue is full.
    CRC_ERROR = -21  #: CRC check failed.
    SECTOR_ERASED = -22  #: Sector unexpectadly erased.
    FILE_ERROR = -23  #: File I/O error.
    DISK_ERROR = -24  #: General disk error.
    DISKFULL_DIR = -25  #: Disk full (directory).
    DISKFULL_DATA = -26  #: Disk full (data).
    SEQ_ERROR = -27  #: Unexpected sequence.
    FILE_SYSTEM_CORRUPT = -28  #: File system corrupt.
    UNSUPPORTED_VERSION = -29  #: Unsupported version.
    NOT_IMPLEMENTED = -30  #: Not implemented.
    FATAL_ERROR = -31  #: Fatal error.
    ILLEGAL_REQUEST = -32  #: Illegal request.
    FILE_NOT_FOUND = -33  #: File not found.
    NOT_FORMATTED = -34  #: Disk not formatted.
    WRONG_DISK_TYPE = -35  #: Wrong disk type.
    TIMEOUT = -36  #: Timeout.
    DEVICE_COMM_ERROR = -37  #: Device communication error.
    OCCUPIED = -38  #: Device occupied.
    USER_CANCEL = -39  #: User abort.
    FIRMWARE = -40  #: Firmware error.
    CONFIG_ERROR = -41  #: Configuration error.
    WRITE_PROT = -42  #: Disk is write protected.
    RESULT_TOO_BIG = -43  #: Result is too big for an out-parameter.


class Device(CEnum):
    """kvmDEVICE_xxx

    Device type, used to connect to a Memorator device.

    """

    MHYDRA = 0  #: Kvaser Memorator (2nd generation)
    MHYDRA_EXT = 1  #: Kvaser Memorator (2nd generation) with extended data capabilities.


class FileType(CEnum):
    """kvmFILE_xxx

    KME file type, a binary file format representing log data.

    """

    KME24 = 0  #: Deprecated format, use KME40
    KME25 = 1  #: Deprecated format, use KME40
    KME40 = 2  #: Kvaser binary format (KME 4.0)
    KME50 = 3  #: Kvaser binary format (KME 5.0)
    KME60 = 4  #: Kvaser binary format (KME 6.0) (Experimental)


class LoggerDataFormat(CEnum):
    """kvmLDF_MAJOR_xxx

    Logged data format (LDF) version.

    """

    MAJOR_CAN = 3  #: Used in Kvaser Memorator (2nd generation)
    MAJOR_CAN64 = 5  #: Used in Kvaser Memorator (2nd generation) with extended data capabilities.


class LogFileType(CEnum):
    """kvmLogFileType_xxx

    .. versionadded:: 1.11

    """

    ERR = 0  #: A log file containing only error frames with frames before and after.
    ALL = 1  #: A log file containing all frames.


class SoftwareInfoItem(CEnum):
    """kvm_SWINFO_xxx

    Different types of version information that can be extracted using
    kvmDeviceGetSoftwareInfo(), used internally by `.Memorator`.

    """

    KVMLIB = 1  #: Returns the version of kvmlib.
    DRIVER = 2  #: Returns the used driver version information.
    FIRMWARE = 3  #: Returns the device firmware version information.
    DRIVER_PRODUCT = 4  #: Obsolete. Returns the product version information.
    CONFIG_VERSION_NEEDED = 5  #: Returns the version of the binary format the device requires (param.lif).
    CPLD_VERSION = 6  #: Obsolete.
