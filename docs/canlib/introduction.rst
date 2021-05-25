Introduction
============

Hello, CAN!
-----------
Let's start with a simple example::

  # The CANlib library is initialized when the canlib module is imported.
  from canlib import canlib, Frame

  # Open a channel to a CAN circuit. In this case we open channel 0 which
  # should be the first channel on the CAN interface. EXCLUSIVE means we don't
  # want to share this channel with any other currently executing program.
  # We also set the CAN bus bit rate to 250 kBit/s, using a set of predefined
  # bus parameters.
  ch = canlib.openChannel(
      channel=0,
      flags=canlib.Open.EXCLUSIVE,
      bitrate=canlib.canBITRATE_250K
  )

  # Set the CAN bus driver type to NORMAL.
  ch.setBusOutputControl(canlib.Driver.NORMAL)

  # Activate the CAN chip.
  ch.busOn()

  # Transmit a message with (11-bit) CAN id = 123, length 6 and contents
  # (decimal) 72, 69, 76, 76, 79, 33.
  frame = Frame(id_=123, data=b'HELLO!', dlc=6)
  ch.write(frame)

  # Wait until the message is sent or at most 500 ms.
  ch.writeSync(timeout=500)

  # Inactivate the CAN chip.
  ch.busOff()

  # Close the channel.
  ch.close()


canlib Core API Calls
---------------------
The following calls can be considered the "core" of canlib as they are essential
for almost any program that uses the CAN bus:

* `canlib.canlib.openChannel` and `canlib.canlib.Channel.close`

* `canlib.canlib.Channel.busOn` and `canlib.canlib.Channel.busOff`

* `canlib.canlib.Channel.read`

* `canlib.canlib.Channel.write` and `canlib.canlib.Channel.writeSync`

