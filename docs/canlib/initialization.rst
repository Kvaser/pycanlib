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
`~canlib.canlib.Channel.writeSync` with a short timeout for each open handle
before closing them with `canlib.canlib.Channel.close`, to ensure the transmit
queues are empty. You can then start afresh by calling
`canlib.canlib.reinitializeLibrary`.

.. note::
   When calling `canlib.canlib.reinitializeLibrary`, all previously opened CAN
   handles (`canlib.canlib.Channel`) will be closed and invalidated.


