import ctypes as ct

from ..cenum import CEnum, CFlag

# In 32-bit Python 2, CFlag enums use C `long`, which is too short to contain
# `EXT`, so fall back on a non-enum in that case
try:

    class MessageFlag(CFlag):
        EXT = 0x80000000  # Message is an extended CAN message
        J1939 = 0x00000001  # Message uses J1939 protocol, currently not used
        WAKEUP = 0x00000002  # Message is a wakeup frame, currently not used


except:

    class MessageFlag(object):
        EXT = 0x80000000  # Message is an extended CAN message
        J1939 = 0x00000001  # Message uses J1939 protocol, currently not used
        WAKEUP = 0x00000002  # Message is a wakeup frame, currently not used

        def __new__(self, val):
            return val


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
    UNKNOWN = 10


class SignalByteOrder(CEnum):
    INTEL = 0
    MOTOROLA = 1


class SignalType(CEnum):
    INVALID = 0
    SIGNED = 1
    UNSIGNED = 2
    FLOAT = 3
    DOUBLE = 4
    _ENUM_SEPARATOR = 100
    ENUM_SIGNED = 101
    ENUM_UNSIGNED = 102


class SignalMultiplexMode(CEnum):
    SIGNAL = 0
    MUX_INDEPENDENT = -1
    MUX_SIGNAL = -2


class AttributeType(CEnum):
    INVALID = 0
    INTEGER = 1
    FLOAT = 3
    ENUM = 4
    STRING = 5


class AttributeOwner(CEnum):
    INVALID = 0
    DB = 1
    MESSAGE = 2
    NODE = 3
    SIGNAL = 4
    ENV = 5


class Error(CEnum):
    FAIL = -1
    NO_DATABASE = -2
    PARAM = -3
    NO_MSG = -4
    NO_SIGNAL = -5
    INTERNAL = -6
    DB_FILE_OPEN = -7
    DATABASE_INTERNAL = -8
    NO_NODE = -9
    NO_ATTRIB = -10
    ONLY_ONE_ALLOWED = -11
    WRONG_OWNER = -12
    IN_USE = -13
    BUFFER_TOO_SMALL = (
        -14
    )  # The buffer provided was not large enough to contain the requested data.
    DB_FILE_PARSE = -15  # Could not parse the database file
