canlib
######

.. toctree::
   :maxdepth: 2


.. contents::

The following sections contain sample code for inspiration on how to use Kvaser Python canlib.


List connected devices
----------------------

This code print some basic information (device name, EAN number and serial number) from all connected devices.

.. code-block:: python

    from canlib import canlib

    num_channels = canlib.getNumberOfChannels()
    print("Found %d channels" % num_channels)
    for ch in range(0, num_channels):
        chdata = canlib.ChannelData(ch)
        print("%d. %s (%s / %s)" % (ch, chdata.device_name,
                                    chdata.card_upc_no,
                                    chdata.card_serial_no))


Send and receive single frame
-----------------------------

Here is some basic code to send and receive a single frame.

.. code-block:: python

    from canlib import canlib, Frame
    from canlib.canlib import ChannelData

    def setUpChannel(channel=0,
                     openFlags=canlib.Open.ACCEPT_VIRTUAL,
                     outputControl=canlib.Driver.NORMAL):
        ch = canlib.openChannel(channel, openFlags)
        print("Using channel: %s, EAN: %s" % (ChannelData(channel).channel_name,
                                              ChannelData(channel).card_upc_no))
        ch.setBusOutputControl(outputControl)
        # Specifying a bus speed of 250 kbit/s. See documentation
        # for more informationon how to set bus parameters.
        params = canlib.busparams.BusParamsTq(
            tq=8,
            phase1=2,
            phase2=2,
            sjw=1,
            prescaler=40,
            prop=3
        )
        ch.set_bus_params_tq(params)
        ch.busOn()
        return ch


    def tearDownChannel(ch):
        ch.busOff()
        ch.close()


    print("canlib version:", canlib.dllversion())

    ch0 = setUpChannel(channel=0)
    ch1 = setUpChannel(channel=1)

    frame = Frame(
        id_=100,
        data=[1, 2, 3, 4],
        flags=canlib.MessageFlag.EXT
    )
    ch1.write(frame)

    while True:
        try:
            frame = ch0.read()
            print(frame)
            break
        except (canlib.canNoMsg) as ex:
            pass
        except (canlib.canError) as ex:
            print(ex)

    tearDownChannel(ch0)
    tearDownChannel(ch1)


Send and receive CAN FD frame
-----------------------------

Here are some minimal code to send and receive a CAN FD frame.

.. code-block:: python

    from canlib import canlib, Frame

    # Specifying an arbitration phase bus speed of 1 Mbit/s,
    # and a data phase bus speed of 2 Mbit/s. See documentation
    # for more information on how to set bus parameters.
    params_arbitration = canlib.busparams.BusParamsTq(
        tq=40,
        phase1=8,
        phase2=8,
        sjw=8,
        prescaler=2,
        prop=23
    )
    params_data = canlib.busparams.BusParamsTq(
        tq=20,
        phase1=15,
        phase2=4,
        sjw=4,
        prescaler=2,
        prop=0
    )

    # open channel as CAN FD using the flag
    ch0 = canlib.openChannel(channel=0, flags=canlib.Open.CAN_FD)
    ch0.setBusOutputControl(drivertype=canlib.Driver.NORMAL)
    ch0.set_bus_params_tq(params_arbitration, params_data)
    ch0.busOn()

    ch1 = canlib.openChannel(channel=1, flags=canlib.Open.CAN_FD)
    ch1.setBusOutputControl(drivertype=canlib.Driver.NORMAL)
    ch1.set_bus_params_tq(params_arbitration, params_data)
    ch1.busOn()

    # set FDF flag to send using CAN FD
    # set BRS flag to send using higher bit rate in the data phase
    frame = Frame(
        id_=100,
        data=range(32),
        flags=canlib.MessageFlag.FDF | canlib.MessageFlag.BRS
    )
    print('Sending', frame)
    ch0.write(frame)

    frame = ch1.read(timeout=1000)
    print('Receiving', frame)

    ch0.busOff()
    ch1.busOff()
