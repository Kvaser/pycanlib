import ctypes as ct


class MessageInfo(ct.Structure):
    """Provides more information about the LIN message.

    The precision of the timing data given in us (microseconds) can be less
    than one microsecond; for low bitrates the lowest bits might always be
    zero.

    The min and max values listed inside [] of the message timing values can be
    calculated from the LIN specification by using the shortest (0 bytes) or
    longest (8 bytes) messages at the lowest or highest allowed bitrate.

    .. note:: The LIN interface will accept messages that are a bit
        out-of-bounds as well.

    .. py:attribute:: timestamp

        Kvaser DRV Lin timestamp - Timestamp in milliseconds of the falling
        edge of the synch break of the message. Uses the canlib CAN timer.

        Kvaser LIN Leaf timestamp - Timestamp in milliseconds of the falling
        edge of the synch break of the message. Uses the canlib CAN timer.

        .. note:: All Kvaser Leaf with Kvaser MagiSync&tm; are synchronized
            (also with CAN channels).

    .. py:attribute:: bitrate

        The bitrate of the message in bits per seconds. Range [1000 .. 20000]
        (plus some margin)

    .. py:attribute:: byteTime

        Start time in microseconds of each data byte. In case of 8-byte
        messages, the crc time isn't included (but can be deduced from
        frameLength).

        .. note:: Not supported by all devices.

    .. py:attribute:: checkSum

        The checksum as read from the LIN bus. Might not match the data in case
        of `MessageFlag.CSUM_ERROR`.

    .. py:attribute:: frameLength

        The total frame length in microseconds; from the synch break to the end
        of the crc. [2200 .. 173600]

    .. py:attribute:: idPar

        The id with parity of the message as read from the LIN bus. Might be
        invalid in case of `MessageFlag.PARITY_ERROR`.

    .. py:attribute:: synchBreakLength

        Length of the synch break in microseconds. [650 .. 13000], [400
        .. 8000] for a wakeup signal.

    .. py:attribute:: synchEdgeTime

        Time in microseconds of the falling edges in the synch byte relative
        the falling edge of the start bit.

        .. note:: Not supported by all devices.

    """
    _fields_ = [
        ("timestamp", ct.c_ulong),
        ("synchBreakLength", ct.c_ulong),
        ("frameLength", ct.c_ulong),
        ("bitrate", ct.c_ulong),
        ("checkSum", ct.c_ubyte),
        ("idPar", ct.c_ubyte),
        ("z", ct.c_ushort),  #: Dummy for alignment
        ("synchEdgeTime", ct.c_ulong * 4),
        ("byteTime", ct.c_ulong * 8),
    ]
