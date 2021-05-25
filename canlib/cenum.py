# use aenum in Python 2.7
try:
    from enum import IntEnum
except:
    from aenum import IntEnum

try:
    from enum import IntFlag
except:
    from aenum import IntFlag


class CEnum(IntEnum):
    """A ctypes-compatible IntEnum superclass."""

    @classmethod
    def from_param(cls, obj):
        return int(obj)


class CFlag(IntFlag):
    """A ctypes-compatible IntFlag superclass."""

    @classmethod
    def from_param(cls, obj):
        return int(obj)
