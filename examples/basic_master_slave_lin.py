"""basic_master_slave_lin.py

This code opens up one master and one slave, sets bitrate and then the slave
sends a wakeup message to the master.

"""

# import the linlib wrapper from the canlib package
from canlib import linlib

# print information about device firmware version
print(linlib.getChannelData(channel_number=0,
                            item=linlib.ChannelData.CARD_FIRMWARE_REV))

# open the first channel as a Master
master = linlib.openChannel(channel_number=0,
                            channel_type=linlib.ChannelType.MASTER)

# open the next channel as a Slave
slave = linlib.openChannel(channel_number=1,
                           channel_type=linlib.ChannelType.SLAVE)

# setup bitrate
master.setBitrate(10000)
slave.setBitrate(10000)

# activate the LIN interface by going bus on
master.busOn()
slave.busOn()

# send a wakeup frame from the slave
slave.writeWakeup()

# read the frame when it arrives at the master
frame = master.read(timeout=100)
print(frame)

# go bus off
master.busOff()
slave.busOff()
