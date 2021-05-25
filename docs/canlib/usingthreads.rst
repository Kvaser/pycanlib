Using Threads
=============

Handles are thread-specific
---------------------------

CANlib supports programs with multiple threads as long as one important
condition is met: A handle to a CAN circuit should be used in only one thread.

This means that you cannot share e.g. `.canlib.Channel` objects between
threads. Each thread has to open its own handle to the circuit.

Also note that you must call `~.canlib.Channel.busOn` and
`~.canlib.Channel.busOff` once for each handle even if the handles are opened
on the same physical channel.


Local echo feature
------------------

If you are using the same channel via multiple handles, note that the default
behaviour is that the different handles will "hear" each other just as if each
handle referred to a channel of its own. If you open, say, channel 0 from
thread A and thread B and then send a message from thread A, it will be
"received" by thread B. This behaviour can be changed using
`~.canlib.IOControl` and `~.canlib.IOControl.local_txecho`.


Init access
-----------

Init access means that the thread that owns the handle can set bit rate and CAN
driver mode. Init access is the default. At most one thread can have init
access to any given channel. If you try to set the bit rate or CAN driver mode
for a handle to which you don't have init access, the call will silently fail,
unless you enable access error reporting by using `~.canlib.IOControl` and
`~.canlib.IOControl.report_access_errors`. Access error reporting is by default
off.


Using the same handle in different threads
------------------------------------------

In spite of what was said above, you can use a single handle in different
threads, provided you create the appropriate mutual exclusion mechanisms
yourself. Two threads should never call CANlib simultaneously unless they are
using different handles.
