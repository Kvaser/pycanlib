from ..cenum import CEnum, CFlag


class Error(CEnum):
    FAIL = -1  #: Generic error.
    PARAM = -2  #: Error in supplied parameters.
    EOF = -3  #: End of input file reached.
    NOT_IMPLEMENTED = -4  #: Not implemented.
    FILE_ERROR = -5  #: File I/O error.
    FILE_EXISTS = -6  #: Output file already exists.
    INTERNAL_ERROR = -7  #: Unhandled internal error.
    NULL_POINTER = -8  #: Unexpected null pointer.
    FILE_TOO_LARGE = -10  #: File size too large for specified format.
    TYPE_MISMATCH = -11  #: Supplied parameter has incorrect type.
    NO_FREE_HANDLES = -12  #: Too many open KvlcHandle handles.
    NO_INPUT_SELECTED = -13  #: Missing call to kvlcSetInputFile or kvlcFeedSelectFormat.
    CONVERTING = -14  #: Call failed since conversion is running.
    BUFFER_SIZE = -15  #: Supplied buffer too small to hold the result.
    INVALID_LOG_EVENT = -30  #: Event is unknown to converter.
    NO_TIME_REFERENCE = -31  #: Required timestamp missing.
    TIME_DECREASING = -32  #: Decreasing time between files.
    MIXED_ENDIANESS = -33  #: Wrong data type in MDF.
    RESULT_TOO_BIG = -34  #: Result is too big for an out-parameter


class FileFormat(CEnum):
    """FILE_FORMAT_xxx

    Format used for input and output, used in `Converter.setInputFile()`.

    Note:
        Not all formats are valid as both output and input format.

    """

    INVALID = 0  #: Invalid file format
    KME24 = 1  #: Input and output file format.
    KME25 = 2  #: Input and output file format.
    VECTOR_ASC = 3  #: Output file format.
    CSV = 4  #: Output file format.
    PLAIN_ASC = 5  #: Output file format.
    MEMO_LOG = 6  #: Input (internal device logfile format).
    KME40 = 7  #: Input and output file format.
    VECTOR_BLF = 8  #: Output file format.
    KME50 = 9  #: Input and output file format.
    KME60 = 10  # Input and output file format.
    CSV_SIGNAL = 100  #: Output file format.
    MDF = 101  #: Output file format.
    MATLAB = 102  #: Output file format.
    J1587 = 103  #: Output file format.
    J1587_ALT = 104  #: Obsolete.
    FAMOS = 105  #: Output file format.
    MDF_SIGNAL = 106  #: Output file format.
    MDF_4X = 107  #: Output file format.
    MDF_4X_SIGNAL = 108  #: Output file format.
    VECTOR_BLF_FD = 109  #: Input and output format.
    DIADEM = 110  #: Output file format.
    RPCIII = 111  #: Output file format.
    XCP = 200  #: Output file format.
    FAMOS_XCP = 201  #: Output file format.
    DEBUG = 1000  #: Reserved for debug.


class ChannelMask(CFlag):
    """Masking channels

    The `ChannelMask` is used in `Converter.addDatabaseFile` to indicate which channels to use.

    Multiple channels may be specified using `|`, e.g. to specify channel one and three use::

        channel_one_and_three = ChannelMask.ONE | ChannelMask.THREE

    .. versionchanged:: 1.20
        Added `ALL` as a convenience.

    """

    ONE = 0x01  #: Mask for first channel
    TWO = 0x02  #: Mask for second channel
    THREE = 0x04  #: Mask for third channel
    FOUR = 0x08  #: Mask for fourth channel
    FIVE = 0x10  #: Mask for fifth channel
    ALL = 0xffff  #: Mask for all channels
