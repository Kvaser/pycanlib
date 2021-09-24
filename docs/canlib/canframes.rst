.. _can-frames:

CAN Frames
==========


CAN Data Frames
---------------

The CAN Data Frame, represented by the `~canlib.Frame` object, is the most
common message type, which consists of the following major parts (a few details
are omitted for the sake of brevity):

CAN identifier: `canlib.Frame.id`
  The CAN identifier, or Arbitration Field, determines the priority of the
  message when two or more nodes are contending for the bus. The CAN identifier
  contains for:

    - CAN 2.0A, an 11-bit Identifier and one bit, the RTR bit, which is
      dominant for data frames.

    - CAN 2.0B, a 29-bit Identifier, with the EXT bit set, (which also contains
      two recessive bits: SRR and IDE) and the RTR bit.

Data field: `canlib.Frame.data`
  The Data field contains zero to eight bytes of data.

Data Length Code: `canlib.Frame.dlc`
  The DLC field specifies the number of data bytes in the Data field.

CRC Field:
  The CRC Field contains a 15-bit checksum calculated on most parts of the
  message. This checksum is used for error detection.

Acknowledgement Slot:
  Any CAN controller that has been able to correctly receive the message sends
  an Acknowledgement bit at the end of each message. The transmitter checks for
  the presence of the Acknowledge bit and retransmits the message if no
  acknowledge was detected.

.. note::
    It is worth noting that the presence of an Acknowledgement Bit on the bus
    does not mean that any of the intended addressees has received the
    message. The only thing we know is that one or more nodes on the bus has
    received it correctly.  The Identifier in the Arbitration Field is not,
    despite of its name, necessarily identifying the contents of the message.

The `canlib.Frame.flags` attribute consists of message information flags,
according to `~canlib.canlib.MessageFlag`.


CAN FD Data Frames
------------------

A standard CAN network is limited to 1 MBit/s, with a maximum payload of 8
bytes per frame. CAN FD increases the effective data-rate by allowing longer
data fields - up to 64 bytes per frame - without changing the CAN physical
layer. CAN FD also retains normal CAN bus arbitration, increasing the bit-rate
by switching to a shorter bit time only at the end of the arbitration process
and returning to a longer bit time at the CRC Delimiter, before the receivers
send their acknowledge bits. A realistic bandwidth gain of 3 to 8 times what's
possible in CAN will particularly benefit flashing applications.


Error Frames
------------

Nearly all hardware platforms support detection of Error Frames. If an Error
Frame arrives, the flag `~canlib.canlib.MessageFlag.ERROR_FRAME` is set in the
`~canlib.Frame`. The identifier is garbage if an Error Frame is received, but
for LAPcan it happens to be 2048 plus the error code from the SJA1000.

Many platforms support transmission of Error Frames as well. To send Error
Frames, set the `~canlib.canlib.MessageFlag.ERROR_FRAME` flag in the
`~canlib.Frame` before sending using `~canlib.canlib.Channel.write`.

Simply put, the Error Frame is a special message that violates the framing
rules of a CAN message. It is transmitted when a node detects a fault and will
cause all other nodes to detect a fault - so they will send Error Frames,
too. The transmitter will then automatically try to retransmit the
message. There is an elaborate scheme of error counters that ensures that a
node can't destroy the bus traffic by repeatedly transmitting error frames.

The Error Frame consists of an Error Flag, which is 6 bits of the same value
(thus violating the bit-stuffing rule) and an Error Delimiter, which is 8
recessive bits. The Error Delimiter provides some space in which the other
nodes on the bus can send their Error Flags when they detect the first Error
Flag.


Remote Requests
---------------

You can send remote requests by passing the `~canlib.canlib.MessageFlag.RTR`
flag to `~canlib.canlib.Channel.write`. Received remote frames are reported by
`~canlib.canlib.Channel.read` et.al. using the same flag.

The Remote Frame is just like the Data Frame, with two important differences:

    - It is explicitly marked as a Remote Frame (the RTR bit in the Arbitration
      Field is recessive)

    - There is no Data Field.

The intended purpose of the Remote Frame is to solicit the transmission of the
corresponding Data Frame. If, say, node A transmits a Remote Frame with the
Arbitration Field set to 234, then node B, if properly initialized, might
respond with a Data Frame with the Arbitration Field also set to 234.

Remote Frames can be used to implement a type of request-response type of bus
traffic management. In practice, however, the Remote Frame is little used. It
is also worth noting that the CAN standard does not prescribe the behaviour
outlined here. Most CAN controllers can be programmed either to automatically
respond to a Remote Frame, or to notify the local CPU instead.

There's one catch with the Remote Frame: the Data Length Code must be set to
the length of the expected response message even though no data is
sent. Otherwise the arbitration will not work.

Sometimes it is claimed that the node responding to the Remote Frame is
starting its transmission as soon as the identifier is recognized, thereby
"filling up" the empty Remote Frame. This is not the case.


Overload Frames
---------------

Overload Frames aren't used nowadays. Certain old CAN controllers (Intel 82526)
used them to delay frame processing in certain cases.


Other frame features of interest
--------------------------------
There are some other frame features of interest:

    - You can send wakeup frames (used for Single-Wire CAN) if your hardware
      supports it, for example, a LAPcan plus a DRVcan S. Just set the
      `~canlib.canlib.MessageFlag.WAKEUP` flag.

    - For "low-speed CAN" (1053/1054 type transceivers), the
      `~canlib.canlib.MessageFlag.NERR` flag is set if a frame is received in
      "fault-tolerant" mode.
