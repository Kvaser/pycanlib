Initialization
==============

Library Initialization
----------------------

The underlaying CANlib library is initialized when the module `canlib.canlib`
is imported.  This will initialize the CANlib library and enumerate all
currently available CAN channels.


Library Deinitialization and Cleanup
------------------------------------

Strictly speaking it is not necessary to clean up anything before terminating
the application. If the application quits unexpectedly, the device driver will
ensure the CAN controller is deactivated and the driver will also ensure the
firmware (if any) is left in a consistent state.

To reinitialize the library in an orderly fashion you may want to call
`.canlib.Channel.writeSync` with a short timeout for each open handle
before closing them with `.canlib.Channel.close`, to ensure the transmit
queues are empty. You can then start afresh by calling
`.canlib.reinitializeLibrary`.

.. note::
   When calling `.canlib.reinitializeLibrary`, all previously opened CAN
   handles (`.canlib.Channel`) will be closed and invalidated.


Manually Enumerating CAN channels
---------------------------------

The function `.canlib.enumerate_hardware` scans all currently connected devices
and creates a completely new set of CANlib channel numbers, while still keeping
all currently opened channel handles valid and usable. This can be viewed upon
as a replacement for calling `.canlib.reinitializeLibrary` which do invalidate
all open channel handles.

One thing to keep in mind when using this functionality is to never track
devices based on their CANlib channel number, since this number may change
anytime `.enumerate_hardware` is called. To retrieve information about a
specific channel use `.Channel.channel_data` to get a safe
`~canlib.canlib.ChannelData`, instead of relying on an old
`~canlib.canlib.ChannelData` object created from a channel number.

.. note:: On Linux, no re-enumeration is needed since enumeration takes place
    when a device is plugged in or unplugged.
