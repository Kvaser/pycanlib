"""request_lin_message.py

Here we look at using LIN 2.0 and setting up a message, using the `Frame`
object, on the slave which is then requested by the master.

"""
from canlib import linlib, Frame


ID = 0x17
DATA = bytearray([1, 2, 3, 4])

# open the first channel as Master, using helper function
master = linlib.openMaster(0, bps=20000)

# open the next channel as a Slave, using helper function
slave = linlib.openSlave(1)

master.busOn()
slave.busOn()

# configure channels to use LIN 2.0
slave.setupLIN(flags=linlib.Setup.ENHANCED_CHECKSUM | linlib.Setup.VARIABLE_DLC)
master.setupLIN(flags=linlib.Setup.ENHANCED_CHECKSUM | linlib.Setup.VARIABLE_DLC)

# setup a message in the slave
slave.updateMessage(Frame(id_=ID, data=DATA))

# request the message and print it
master.requestMessage(ID)
frame = master.read(timeout=100)
print(frame)

# clear the message
slave.clearMessage(0x17)

# we should now get an empty message
master.requestMessage(0x17)
frame = master.read(timeout=100)
print(frame)

# go bus off
master.busOff()
slave.busOff()
