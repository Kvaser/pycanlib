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
    bitrate=canlib.Bitrate.BITRATE_250K,
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
