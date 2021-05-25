linlib
######

.. toctree::
   :maxdepth: 2


The following sections contain sample code for inspiration on how to use Kvaser Python linlib.


Basic master slave usage
------------------------

This code opens up one master and one slave, sets bitrate and then the slave sends a wakeup message to the master.

.. code-block:: python

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


Sending message from master
---------------------------

Our next example uses two shorthand helper functions to open the channels. We then send some messages from the master and see that they arrive.

.. code-block:: python

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


Requesting LIN 2.0 message
--------------------------

As a last example, let’s look at using LIN 2.0 and setting up a message, using the `Frame` object, on the slave which is then requested by the master.

.. code-block:: python

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
