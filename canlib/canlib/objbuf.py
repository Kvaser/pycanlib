"""Support for accessing Object Buffers.

.. versionadded:: 1.22

"""
from ..cenum import CEnum
from . import wrapper

dll = wrapper.dll
canOBJBUF_AUTO_RESPONSE_RTR_ONLY = 0x01


class MessageFilter:
    """A message reception filter.

    First set the mask bit to '1' for the bits you would like to filter
    on. Then set the code to the desired bitpattern.
    See :ref:`code_and_mask_format` for an explanation of the *code and mask* format.

    Calling the `MessageFilter` with an id returns `True` if the id passes the filter.

      >>> mf = MessageFilter(code=0b0100, mask=0b0110)
      >>> mf(0b0110)
      False

      >>> mf(0b0101)
      True

      >>> mf(0b0010)
      False

    For use with `.Response` object buffers.

    .. versionadded:: 1.22

    """
    def __init__(self, code, mask):
        self.code = code
        self.mask = mask

    def __call__(self, msg_id):
        return not ((msg_id ^ self.code) & self.mask)


class Type(CEnum):
    """An enumeration based on canOBJBUF_TYPE_xxx"""
    AUTO_RESPONSE = 1  #: The buffer is an auto response buffer.
    PERIODIC_TX = 2  #: The buffer is an auto transmit buffer.


class ObjectBuffer:
    def __repr__(self):
        return f"<{type(self).__module__}.{type(self).__name__} idx:{self.idx}>"

    def disable(self):
        """Disable this object buffer."""
        dll.canObjBufDisable(self.ch.handle, self.idx)

    def enable(self):
        """Enable this object buffer."""
        dll.canObjBufEnable(self.ch.handle, self.idx)

    def free(self):
        """Deallocate this object buffer.

        This object buffer can not be referenced after this operation.
        To free all allocated object buffers, use `.canlib.Channel.free_objbuf()`.

        """
        if self.ch is not None:
            dll.canObjBufFree(self.ch.handle, self.idx)
            self.idx = -1
            self.ch = None

    def set_frame(self, frame):
        """Define the CAN frame to be sent by the object buffer.

        Args:
            frame (`~canlib.Frame`): The CAN frame to send.

        """
        self.frame = frame
        dll.canObjBufWrite(self.ch.handle, self.idx, frame.id, bytes(frame.data), frame.dlc, frame.flags)


class Periodic(ObjectBuffer):
    """Periodic object buffer (also known as auto transmit buffer).

    Returned from `.canlib.Channel.allocate_periodic_objbuf()`

    """
    def __init__(self, ch, period_us, frame=None):
        self.count = 0
        # Initialize idx and ch here in case canObjBufAllocate triggers an exception.
        self.idx = -1
        self.ch = None
        self.idx = dll.canObjBufAllocate(ch.handle, Type.PERIODIC_TX)
        self.ch = ch
        if frame is not None:
            self.set_frame(frame)
        self.set_period(period_us)

    def enable(self):
        """Enable this object buffer."""
        self.set_msg_count(count=None)
        super().enable()

    def set_period(self, period_us):
        """Set interval in microseconds between each sent CAN frame.

        Args:
            period_us (`int`): Interval in microseconds between each sent CAN frames.

        """

        dll.canObjBufSetPeriod(self.ch.handle, self.idx, period_us)
        self.period_us = period_us

    def send_burst(self, length):
        """Send a burst of CAN frames from this object buffer.

        The frames will be sent as fast as possible from the hardware.
        This function is intended for certain diagnostic applications.

        Args:
            length (`int`): Number of CAN frames to send.

        """
        dll.canObjBufSendBurst(self.ch.handle, self.idx, length)

    def set_msg_count(self, count):
        """Limit the total number of CAN frames sent.

        When this periodic buffer is enabled, only `count` number of CAN frames
        will be sent (i.e. the periodic buffer will only be active for `count`
        number of periods).

        When all frames have been sent, the msg_count is set to zero. If you
        would like to send five more frames, you need to make two calls::

            >>> periodic_buffer.set_msg_count(5)
            >>> periodic_buffer.enable()

        Args:
            count (`int`): Total number of CAN frames to send, Zero means infinite.

        """
        if count is not None:
            self.count = count
        dll.canObjBufSetMsgCount(self.ch.handle, self.idx, self.count)


class Response(ObjectBuffer):
    """Auto response object buffer.

    Returned from `.canlib.Channel.allocate_response_objbuf()`

    The following example responds with a CAN frame with CAN ID 200 when a CAN
    frame with CAN ID 100 is received.::

        >>> from canlib import canlib, Frame
        >>> ch = canlib.openChannel(0)
        >>> msg_filter = canlib.objbuf.MessageFilter(code=100, mask=0xFFFF)
        >>> msg_filter(100)
        True
        >>> frame = Frame(id_=200, data=[1, 2, 3, 4])
        >>> response_buf = ch.allocate_response_objbuf(filter=msg_filter, frame=frame)
        >>> response_buf.enable()

    .. versionadded:: 1.22

    """
    def __init__(self, ch, filter=None, frame=None, rtr_only=False):
        # Initialize idx and ch here in case canObjBufAllocate triggers an exception.
        self.idx = -1
        self.ch = None
        self.idx = dll.canObjBufAllocate(ch.handle, Type.AUTO_RESPONSE)
        self.ch = ch
        if frame is not None:
            self.set_frame(frame)
        if filter is not None:
            self.set_filter(filter)
        if rtr_only:
            self.set_rtr_only(True)

    def set_filter(self, filter):
        """Set message reception filter.

        If no filter is set, any CAN ID will trigger the auto response.

        Args:
            filter (`MessageFilter`): Messages not matching the filter is ignored.

        """
        dll.canObjBufSetFilter(self.ch.handle, self.idx, filter.code, filter.mask)
        self.filter = filter

    def set_rtr_only(self, value):
        """Filter on CAN RTR (remote transmission request).

        This complements the message reception filter (see `set_filter()`).

        When set to `True`, the auto response buffer will only respond to
        remote requests (that also passes the message reception filter).  When set to
        `False`, the auto response buffer will respond to both remote requests
        and ordinary data frames (that also passes the message reception filter).

        """
        if value:
            flags = canOBJBUF_AUTO_RESPONSE_RTR_ONLY
        else:
            flags = 0
        dll.canObjBufSetFlags(self.ch.handle, self.idx, flags)
