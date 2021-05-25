from ..cenum import CEnum


class Error(CEnum):
    FAIL = -1
    PARAM = -3
    LOGFILEOPEN = -8
    NOSTARTTIME = -9
    NOLOGMSG = -10
    LOGFILEWRITE = -11
    EOF = -12
    NO_DISK = -13
    LOGFILEREAD = -14
    QUEUE_FULL = -20
    CRC_ERROR = -21
    SECTOR_ERASED = -22
    FILE_ERROR = -23
    DISK_ERROR = -24
    DISKFULL_DIR = -25
    DISKFULL_DATA = -26
    SEQ_ERROR = -27
    FILE_SYSTEM_CORRUPT = -28
    UNSUPPORTED_VERSION = -29
    NOT_IMPLEMENTED = -30
    FATAL_ERROR = -31
    ILLEGAL_REQUEST = -32
    FILE_NOT_FOUND = -33
    NOT_FORMATTED = -34
    WRONG_DISK_TYPE = -35
    TIMEOUT = -36
    DEVICE_COMM_ERROR = -37
    OCCUPIED = -38
    USER_CANCEL = -39
    FIRMWARE = -40
    CONFIG_ERROR = -41
    WRITE_PROT = -42
    RESULT_TOO_BIG = -43


class Device(CEnum):
    """kvmDEVICE_xxx

    Device type, used to connect to a Memorator device.

    """

    MHYDRA = 0
    MHYDRA_EXT = 1


class FileType(CEnum):
    """kvmFILE_xxx

    KME file type, a binary file format representing log data.

    """

    KME24 = 0  # Deprecated format, use KME40
    KME25 = 1  # Deprecated format, use KME40
    KME40 = 2
    KME50 = 3


class LoggerDataFormat(CEnum):
    """kvmLDF_MAJOR_xxx

    Logged data format (LDF) version.

    """

    MAJOR_CAN = 3  # Used in Kvaser Memorator (2nd generation)
    MAJOR_CAN64 = 5  # Used in Kvaser Memorator (2nd generation) with
    # extended data capabilities.


class LogFileType(CEnum):
    """kvmLogFileType_xxx

    .. versionadded:: 1.11

    """

    ERR = 0  # A log file containing only error frames with frames before and after.
    ALL = 1  # A log file containing all frames.


class SoftwareInfoItem(CEnum):
    """kvm_SWINFO_xxx

    Different types of version information that can be extracted using
    kvmDeviceGetSoftwareInfo().

    """

    KVMLIB = 1
    DRIVER = 2
    FIRMWARE = 3
    CONFIG_VERSION_NEEDED = 5
