Introduction
============

Hello, CAN!
-----------
Let's start with a simple example:

.. literalinclude:: /../examples/hello_can.py



canlib Core API Calls
---------------------
The following calls can be considered the "core" of canlib as they are essential
for almost any program that uses the CAN bus:

* `~canlib.canlib.openChannel` and `~canlib.canlib.Channel.close`

* `~canlib.canlib.Channel.busOn` and `~canlib.canlib.Channel.busOff`

* `~canlib.canlib.Channel.read`

* `~canlib.canlib.Channel.write` and `~canlib.canlib.Channel.writeSync`

