from .. import deprecation
from . import channel


@deprecation.deprecated.cls("canlib.Channel")
class canChannel(channel.Channel):
    """Deprecated name for Channel

    canChannel has been renamed to Channel, using the old name (canChannel) is
    deprecated.

    Note that the CANLib class has also been deprecated, so instantiating a
    Channel object doesn't need a CANLib object as the first argument. To keep
    this class backwards compatible, the `canlib` argument when initializing
    `canChannel` objects is now ignored.

    See `canlib.CANLib` for more details about the deprecation.

    """

    def __init__(self, canlib, channel, flags=0):
        super().__init__(channel, flags)
