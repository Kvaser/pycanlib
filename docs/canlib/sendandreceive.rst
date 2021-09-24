Send and Receive
================

Bus On / Bus Off
----------------

When the CAN controller is on bus, it is receiving messages and is sending
acknowledge bits in response to all correctly received messages. A controller
that is off bus is not taking part in the bus communication at all.

When you have a `~canlib.canlib.Channel` object, use
`~canlib.canlib.Channel.busOn` to go on bus and `~canlib.canlib.Channel.busOff`
to go off bus.

If you have multiple `~canlib.canlib.Channel` objects to the same controller,
the controller will go off bus when the last of the `~canlib.canlib.Channel`
objects go off bus (i.e. all `~canlib.canlib.Channel` objects must be off bus
for the controller to be off bus). You can use
`~canlib.canlib.Channel.readStatus` and watch the flag
`~canlib.canlib.Stat.BUS_OFF` to see if the controller has gone off
bus.

You can set a channel to silent mode by using the `~canlib.Driver.SILENT` mode
if you want it to be on-bus without interfering with the traffic in any way,
see :ref:`can-driver-modes`.

This example opens a channel, takes it on-bus, then takes it off-bus and closes it::

    >>> from canlib import canlib
    ... with canlib.openChannel(channel=1) as ch:
    ...     ch.busOn()
    ...     ...
    ...     ch.busOff()


Reading Messages
----------------

Incoming messages are placed in a queue in the driver. In most cases the
hardware does message buffering as well. You can read the first message in the
queue by calling `~canlib.canlib.Channel.read`, which will raise the exception
`~canlib.canlib.CanNoMsg` if there was no message available.

The `~canlib.Frame.flags` attribute of the `~canlib.Frame` returned by
`~canlib.canlib.Channel.read` contains a combination of the
`~canlib.canlib.MessageFlag` flags, including `~canlib.canlib.MessageFlag.FDF`,
`~canlib.canlib.MessageFlag.BRS`, and `~canlib.canlib.MessageFlag.ESI` if the
CAN FD protocol is enabled, and error flags such as
`~canlib.canlib.MessageFlag.OVERRUN` which provides you with more information
about the message; for example, a frame with a 29-bit identifier will have the
`~canlib.canlib.MessageFlag.EXT` bit set, and a remote frame will have the
`~canlib.canlib.MessageFlag.RTR` bit set. Note that the flag argument is a
combination of the `~canlib.canlib.MessageFlag`, so more than one flag might be
set.

See :ref:`can-frames` for more information.

.. qqqmac Add when target page is done
   The size of the queues in the driver and hardware is described in Message Queue and Buffer Sizes.

Sometimes it is desirable to have a peek into the more remote parts of the
queue. Is there, for example, any message waiting that has a certain
identifier?

    ..
       - `~canlib.canlib.Channel.readSyncSpecific` - You can call
         canReadSpecific() to read that message. Messages not matching the
         specified identifier will be kept in the queue and will be returned on
         the next call to canRead().

    - If you want to read just a message with a specified identifier, and throw
      all others away, you can call
      `~canlib.canlib.Channel.readSpecificSkip`. This routine will return the
      first message with the specified identifier, discarding any other message
      in front of the desired one.

    - If you want to wait until a message arrives (or a timeout occurs) and
      then read it, call `~canlib.canlib.Channel.read` with a timeout.

    - If you want to wait until there is at least one message in the queue with
      a certain identifier, but you don't want to read it, call
      `~canlib.canlib.Channel.readSyncSpecific`.

The following code fragment reads the next available CAN message, (using
default bitrate 500 kbit/s)::

    >>> from canlib import canlib
    ... with canlib.openChannel(channel=0) as ch:
    ...     ch.busOn()
    ...     frame = ch.read(timeout=1000)
    ...     ch.busOff()
    >>> frame
    Frame(id=709, data=bytearray(b'\xb5R'), dlc=2, flags=<MessageFlag.STD: 2>, timestamp=3)


Acceptance Filters
------------------

You can set filters to reduce the number of received messages. CANlib supports
setting of the hardware filters on the CAN interface board. This is done with
the `~canlib.canlib.Channel.canAccept` function.

You set an acceptance code and an acceptance mask which together determine
which CAN identifiers are accepted or rejected.

If you want to remove an acceptance filter, call
`~canlib.canlib.Channel.canAccept` with the mask set to
`~canlib.AcceptFilterFlag.NULL_MASK`.

To set the mask to 0xF0 and the code to 0x60::

    >>> from canlib import canlib
    >>> ch = canlib.openChannel(channel=0)
    >>> ch.canAccept(0x0f0, canlib.AcceptFilterFlag.SET_MASK_STD)
    >>> ch.canAccept(0x060, canlib.AcceptFilterFlag.SET_CODE_STD)
    >>> ...
    >>> ch.close()


This code snippet will cause all messages having a standard (11-bit) identifier
with bit 7 - bit 4 in the identifier equal to 0110 (binary) will pass
through. Other messages with standard identifiers will be rejected.

How acceptance filters can be used in a smaller project::

  >>> from canlib import canlib
  >>> ch = canlib.openChannel(channel=0)
  >>> # The acceptance filter only have to be called once for each ch object
  >>> ch.canAccept(0x0f0, canlib.AcceptFilterFlag.SET_MASK_STD)
  >>> ch.canAccept(0x060, canlib.AcceptFilterFlag.SET_CODE_STD)
  >>> ...
  >>> # We can now run the rest of the program and the acceptance filter
  >>> # will reject unwanted CAN messages.
  >>> while(True):
  >>>     frame = ch.read()
  >>>     ...
  >>> ...


Code and Mask Format
^^^^^^^^^^^^^^^^^^^^
Explanation of the code and mask format used by the `~canlib.canlib.Channel.canAccept` function:

    A binary 1 in a mask means "the corresponding bit in the code is relevant"
    A binary 0 in a mask means "the corresponding bit in the code is not relevant"
    A relevant binary 1 in a code means "the corresponding bit in the identifier must be 1"
    A relevant binary 0 in a code means "the corresponding bit in the identifier must be 0"

In other words, the message is accepted if ((code XOR id) AND mask) == 0.

.. :note:

    You can set the extended code and mask only on CAN boards that support
    extended identifiers.  Not all CAN boards support different masks for
    standard and extended CAN identifiers. On some boards
    the acceptance filtering is done by the CAN hardware; on other boards
    (typically those with an embedded CPU,) the acceptance filtering is done by
    software. `~canlib.canlib.Channel.canAccept` behaves in the same way for all
    boards, however.


Sending Messages
----------------

You transmit messages by calling `~canlib.canlib.Channel.write`. Outgoing CAN messages are buffered
in a transmit queue and sent on a First-In First-Out basis. You can use
`~canlib.canlib.Channel.writeSync` to wait until the messages in the queue have been sent.

Sending a CAN message::

    >>> from canlib import canlib, Frame
    ... with canlib.openChannel(channel=0) as ch:
    ...     ch.busOn()
    ...     frame = Frame(id_=234, data=[1,2])
    ...     ch.write(frame)
    ...     ch.busOff()


Using Extended CAN (CAN 2.0B)
-----------------------------

"Standard" CAN has 11-bit identifiers in the range 0 - 2047. "Extended" CAN,
also called CAN 2.0B, has 29-bit identifiers. You specify which kind of
identifiers you want to use in your call to canWrite(): if you set the
`~canlib.MessageFlag.EXT` flag in the flag argument, the message will be
transmitted with a 29-bit identifier. Conversely, received 29-bit-identifier
messages have the `~canlib.MessageFlag.EXT` flag set.

The following code fragment sends a CAN message on an already open channel. The
CAN message will have identifier 1234 (extended) and DLC = 8. The contents of
the data bytes will be whatever the data array happens to contain::

    >>> frame = Frame(id_=1234, data=[1,2,3,4,5,6,7,8], flags=canlib.MessageFlag.EXT)
    >>> frame
    Frame(id=1234, data=bytearray(b'\x01\x02\x03\x04\x05\x06\x07\x08'), dlc=8, flags=<MessageFlag.EXT: 4>, timestamp=None)
    >>> ch.write(frame)


Object Buffers
--------------

Object buffers are currently not supported in the Python wrapper.
