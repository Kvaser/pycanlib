"""send_lin_message.py

This example uses two shorthand helper functions to open the channels. We then
send some messages from the master and see that they arrive.

"""
from canlib import linlib, Frame

# open the first channel as Master, using helper function
master = linlib.openMaster(0)

# open the next channel as a Slave, using helper function
slave = linlib.openSlave(1)

# go bus on
master.busOn()
slave.busOn()

# send some messages from master
NUM_MESSAGES = 2
for i in range(NUM_MESSAGES):
    master.writeMessage(Frame(id_=i, data=[1, 2, 3, 4, 5, 6, 7, 8]))
master.writeSync(100)

# print the received messages at the slave
for i in range(NUM_MESSAGES):
    frame = slave.read(timeout=100)
    print(frame)

# the master should also have recorded the messages
for i in range(NUM_MESSAGES):
    frame = master.read(timeout=100)
    print(frame)

# go bus off
master.busOff()
slave.busOff()
