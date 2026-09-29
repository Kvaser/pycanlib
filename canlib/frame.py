def dlc_to_bytes(dlc, canFd=False):
    """Convert DLC to number of bytes

    .. versionadded:: 1.7

    """
    if dlc < 9:
        bytes = dlc
    elif dlc == 9:
        bytes = 12
    elif dlc == 10:
        bytes = 16
    elif dlc == 11:
        bytes = 20
    elif dlc == 12:
        bytes = 24
    elif dlc == 13:
        bytes = 32
    elif dlc == 14:
        bytes = 48
    else:
        bytes = 64

    if canFd:
        return bytes
    else:
        return min(bytes, 8)


def bytes_to_dlc(num_bytes, canFD=True):
    """Calculate minimum DLC that can hold number of bytes

    .. versionadded:: 1.18

    """
    if not canFD:
        return num_bytes
    if num_bytes < 8:
        return num_bytes
    if num_bytes <= 12:
        return 9
    if num_bytes <= 16:
        return 10
    if num_bytes <= 20:
        return 11
    if num_bytes <= 24:
        return 12
    if num_bytes <= 32:
        return 13
    if num_bytes <= 48:
        return 14
    return 15


class Frame:
    """Represents a CAN message

    Args:
        id_: Message id
        data : Message data, will pad zero to match dlc (if dlc is given)
        dlc : Message dlc, default is calculated from number of data
        flags (`canlib.MessageFlag`): Message flags, default is 0
        timestamp : Optional timestamp
    """  # noqa: RST306

    __slots__ = ('id', 'data', 'dlc', 'flags', 'timestamp')
    _repr_slots = __slots__
    _eq_slots = __slots__[:-1]

    def __init__(self, id_, data, dlc=None, flags=0, timestamp=None):
        data = bytearray(data)

        if dlc is None:
            if len(data) <= 8:
                dlc = len(data)
            elif len(data) <= 12:
                dlc = 12
            elif len(data) <= 16:
                dlc = 16
            elif len(data) <= 20:
                dlc = 20
            elif len(data) <= 24:
                dlc = 24
            elif len(data) <= 32:
                dlc = 32
            elif len(data) <= 48:
                dlc = 48
            else:
                dlc = 64
            if dlc > len(data):
                data.extend([0] * (dlc - len(data)))
        elif dlc <= 8:
            data.extend([0] * (dlc - len(data)))

        self.id = id_
        self.data = data
        self.dlc = dlc
        self.flags = flags
        self.timestamp = timestamp

    # in Python 2 both __eq__ and __ne__ must be implemented
    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        if isinstance(other, Frame):
            return all(getattr(self, slot) == getattr(other, slot) for slot in self._eq_slots)
        else:
            return NotImplemented

    def __getitem__(self, index):
        slot = self.__slots__[index]
        return getattr(self, slot)

    def __setitem__(self, index, val):
        slot = self.__slots__[index]
        return setattr(self, slot, val)

    def __iter__(self):
        for slot in self.__slots__:
            yield getattr(self, slot)

    def __repr__(self):
        return '{cls}({kwargs})'.format(
            cls=self.__class__.__name__,
            kwargs=', '.join(slot + '=' + repr(getattr(self, slot)) for slot in self._repr_slots),
        )


class LINFrame(Frame):
    """Represents a LIN message

    A `Frame` that also has an `info` attribute, which is a
    `linlib.MessageInfo` or `None`. This attribute is initialized via the `info`
    keyword-only argument to the constructor.

    """

    __slots__ = Frame.__slots__ + ('info',)

    # In python 3 we could just use:
    #
    # def __init__(self, *args, info=None, **kwargs):
    def __init__(self, *args, **kwargs):
        info = kwargs.pop("info", None)
        if 'timestamp' not in kwargs and info is not None:
            kwargs['timestamp'] = info.timestamp
        super().__init__(*args, **kwargs)
        self.info = info
