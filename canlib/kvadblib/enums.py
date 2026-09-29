import ctypes as ct

from ..cenum import CEnum, CFlag


class MessageFlag(CFlag):
    EXT = 0x80000000  #: Message is an extended CAN message
    J1939 = 0x00000001  #: Message uses J1939 protocol
    WAKEUP = 0x00000002  #: Message is a wakeup frame, currently not used


class ProtocolProperties(ct.Structure):
    _fields_ = [
        ("maxMessageDlc", ct.c_uint),
        ("maxSignalLength", ct.c_uint),
    ]


class ProtocolType(CEnum):
    CAN = 0
    VAN = 1
    LIN = 2
    MOST = 3
    FLEXRAY = 4
    BEAN = 5
    ETHERNET = 6
    AFDX = 7
    J1708 = 8
    CANFD = 9
    UNKNOWN = 10  #: Unknown or not specified protocol


class SignalByteOrder(CEnum):
    INTEL = 0
    MOTOROLA = 1


class SignalType(CEnum):
    INVALID = 0  #: Invalid representation
    SIGNED = 1  #: Signed integer
    UNSIGNED = 2  #: Unsigned integer
    FLOAT = 3  #: Float, strictly 32 bit long
    DOUBLE = 4  #: Double, strictly 64 bit long
    _ENUM_SEPARATOR = 100
    ENUM_SIGNED = 101
    ENUM_UNSIGNED = 102


class SignalMultiplexMode(CEnum):
    SIGNAL = 0
    MUX_INDEPENDENT = -1  #: Multiplex mode value of an independent signal
    MUX_SIGNAL = -2  #: Multiplex mode value of a multiplexer signal


class AttributeType(CEnum):
    INVALID = 0
    INTEGER = 1
    HEX = 2
    FLOAT = 3
    ENUM = 4
    STRING = 5


class AttributeOwner(CEnum):
    INVALID = 0  #: Invalid owner
    DB = 1  #: Database owner
    MESSAGE = 2  #: Message owner
    NODE = 3  #: Node owner
    SIGNAL = 4  #: Signal owner
    ENV = 5  #: Environment owner


class Error(CEnum):
    """kvaDbErr_xxx"""
    FAIL = -1  #: General failure.
    NO_DATABASE = -2  #: No database was found.
    PARAM = -3  #: One or more of the parameters in call is erronous.
    NO_MSG = -4  #: No message was found.
    NO_SIGNAL = -5  #: No signal was found.
    INTERNAL = -6  #: An internal error occured in the library.
    DB_FILE_OPEN = -7  #: Could not open the database file.
    DATABASE_INTERNAL = -8  #: An internal error occured in the database handler.
    NO_NODE = -9  #: Could not find the database node.
    NO_ATTRIB = -10  #: No attribute found
    ONLY_ONE_ALLOWED = -11
    """An identical kvaDbLib structure already exists (and only one database at a time can be used)."""
    WRONG_OWNER = -12  #: Wrong owner for attribute
    IN_USE = -13  #: An item is in use
    BUFFER_TOO_SMALL = -14
    """The buffer provided was not large enough to contain the requested data."""
    DB_FILE_PARSE = -15  #: Could not parse the database file
