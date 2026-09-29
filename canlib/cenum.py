from enum import IntEnum
from enum import IntFlag


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
