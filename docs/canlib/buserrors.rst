Bus Errors
==========

Obtaining Bus Status Information
--------------------------------

Use `~canlib.canlib.Channel.read_error_counters` to read the error counters of
the CAN controller. There are two such counters in a CAN controller (they are
required by the protocol definition). Not all CAN controllers allow access to
the error counters, so CANlib may provide you with an "educated guess" instead.

Use `~canlib.canlib.Channel.readStatus` to obtain the bus status (error active,
error passive, bus off; as defined by the CAN standard).


Overruns
--------

If the CAN interface or the driver runs out of buffer space, or if the bus load
is so high that the CAN controller can't keep up with the traffic, an overload
condition is flagged to the application.

The driver will set the `~.MessageFlag.HW_OVERRUN` and/or
`~.MessageFlag.SW_OVERRUN` flags in the flag argument of `~.canlib.Channel.read` and
its relatives. The flag(s) will be set in the first message read from the
driver after the overrun or overload condition happened.

Not all hardware platforms can detect the difference between hardware overruns
and software overruns, so your application should test for both conditions. You
can use the symbol `~.MessageFlag.OVERRUN` for this purpose.


Error Frames
------------

When a CAN controller detects an error, it transmits an error frame. This is a
special CAN message that causes all other CAN controllers on the bus to notice
that an error has occurred.

CANlib will report error frames to the application just like it reports any
other CAN message, but the `~.MessageFlag.ERROR_FRAME` flag will be set in the
flags parameter when e.g. `~.canlib.Channel.read` returns.

When an error frame is received, its identifier, DLC and data bytes will be
undefined. You should test if a message is an error frame before checking its
identifier, DLC or data bytes.

In an healthy CAN system, error frames should rarely, if ever, occur. Error
frames usually mean there is some type of serious problem in the system, such
as a bad connector, a bad cable, bus termination missing or faulty, or another
node transmitting at wrong bit rate, and so on.
