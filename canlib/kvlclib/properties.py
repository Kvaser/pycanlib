import ctypes as ct

from ..cenum import CEnum


class Property(CEnum):
    START_OF_MEASUREMENT = 1  #: Use start of measurement as time reference.
    FIRST_TRIGGER = 2  #: Use first trigger as time reference.
    USE_OFFSET = 3  #: Use offset as time reference.
    OFFSET = 4  #: Time reference offset.
    CHANNEL_MASK = 5  #: Bitmask of the channels that should be used during conversion.

    HLP_J1939 = 6  #: Interpret events as J1939.
    CALENDAR_TIME_STAMPS = 7  #: Write calendar time stamps.
    WRITE_HEADER = 8  #: Write informational header.
    SEPARATOR_CHAR = 9  #: Use token as separator.
    DECIMAL_CHAR = 10  #: Use token as decimal separator.

    ID_IN_HEX = 11  #: Write id in hexadecimal format.
    DATA_IN_HEX = 12  #: Write data in hexadecimal format.
    NUMBER_OF_TIME_DECIMALS = 13  #: Number of time decimals (0-9).
    NAME_MANGLING = 14  #: Make signal names safe for use in Matlab.
    FILL_BLANKS = 15  #: Propagate values down to next row in csv-files.

    SHOW_UNITS = 16  #: Show units on their own row.
    ISO8601_DECIMALS = 17
    """Number of time decimals (0-9) to print in the calendar timestamps using ISO8601."""

    MERGE_LINES = 18  #: Merge two lines if their signal values are equal.
    RESAMPLE_COLUMN = 19  #: Only print a line when the given column has been accessed.
    VERSION = 20  #: File format version.

    SHOW_COUNTER = 21  #: Add a counter to the output.
    CROP_PRETRIGGER = 22  #: Crop pre-triggers.
    ENUM_VALUES = 23  #: Replace integer values in signals with strings from database.
    SIZE_LIMIT = 24  #: Maximum file size in megabytes before starting a new output file.
    TIME_LIMIT = 25
    """Maximum delta time in seconds between first and last event before starting a new output file."""

    LIMIT_DATA_BYTES = 26  #: Number of data bytes that a converter will write.
    CREATION_DATE = 27
    """File creation date/time as seconds in standard UNIX format. Used in file headers if not zero."""
    OVERWRITE = 28  #: Overwrite existing output files
    TIMEZONE = 29  #: Timezone for absolute timestamps
    FULLY_QUALIFIED_NAMES = 30  #: Write fully qualified signal names
    NUMBER_OF_DATA_DECIMALS = 31  #: Number of data decimals (0-50)
    COMPRESSION_LEVEL = 32
    """ZLIB compression level for writers that use ZLIB for compression. [-1, 9]."""
    SAMPLE_AND_HOLD_TIMESTEP = 33
    """Time step in microseconds.

    Used for format where time is implicit and defined by start time and the
    selected time step in microseconds. Signal values are interpolated with sample
    and hold. Used with e.g. DIAdem and RPCIII."""

    SIGNAL_BASED = 1001
    """Writes signals and not data frames.

    Used only with `WriterFormat.isPropertySupported()` and
    `ReaderFormat.isPropertySupported()`.

    """
    SHOW_SIGNAL_SELECT = 1002
    """Format requires a database.

    Used only with `WriterFormat.isPropertySupported()` and
    `ReaderFormat.isPropertySupported()`.

    """
    ATTACHMENTS = 1003
    """Can attach files to converted data.

    It is possible to use `Converter.attachFile()` to add a file. Used only
    with `WriterFormat.isPropertySupported()` and
    `ReaderFormat.isPropertySupported()`.

    """


_PROPERTY_TYPE = {
    Property.START_OF_MEASUREMENT: ct.c_int,
    Property.FIRST_TRIGGER: ct.c_int,
    Property.USE_OFFSET: ct.c_int,
    Property.OFFSET: ct.c_int64,
    Property.CHANNEL_MASK: ct.c_uint,
    Property.HLP_J1939: ct.c_int,
    Property.CALENDAR_TIME_STAMPS: ct.c_int,
    Property.WRITE_HEADER: ct.c_int,
    Property.SEPARATOR_CHAR: ct.c_char,
    Property.DECIMAL_CHAR: ct.c_char,
    Property.ID_IN_HEX: ct.c_int,
    Property.DATA_IN_HEX: ct.c_int,
    Property.NUMBER_OF_TIME_DECIMALS: ct.c_int,
    Property.NAME_MANGLING: ct.c_int,
    Property.FILL_BLANKS: ct.c_int,
    Property.SHOW_UNITS: ct.c_int,
    Property.ISO8601_DECIMALS: ct.c_int,
    Property.MERGE_LINES: ct.c_int,
    Property.RESAMPLE_COLUMN: ct.c_int,
    Property.VERSION: ct.c_int,
    Property.SHOW_COUNTER: ct.c_int,
    Property.CROP_PRETRIGGER: ct.c_int,
    Property.ENUM_VALUES: ct.c_int,
    Property.SIZE_LIMIT: ct.c_uint,
    Property.TIME_LIMIT: ct.c_uint,
    Property.LIMIT_DATA_BYTES: ct.c_int,
    Property.CREATION_DATE: ct.c_int64,
    Property.OVERWRITE: ct.c_int,
    Property.TIMEZONE: ct.c_int,
    Property.FULLY_QUALIFIED_NAMES: ct.c_int,
    Property.NUMBER_OF_DATA_DECIMALS: ct.c_int,
    Property.COMPRESSION_LEVEL: ct.c_int,
    Property.SAMPLE_AND_HOLD_TIMESTEP: ct.c_int,
    Property.SIGNAL_BASED: None,
    Property.SHOW_SIGNAL_SELECT: None,
    Property.ATTACHMENTS: None,
}
