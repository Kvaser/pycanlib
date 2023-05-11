Time Domain
==================


Resetting device clocks
-----------------------
When a group of channels are added to a Time Domain, their clocks can
be reset through a call to `~canlib.canlib.TimeDomain.reset_time`.
This function does not require MagiSync support.

Resetting device clocks:

.. code-block:: python

    from canlib import canlib, Frame

    ch_tx = canlib.openChannel(0)
    ch_rx1 = canlib.openChannel(1)
    ch_rx2 = canlib.openChannel(2)

    domain = canlib.TimeDomain()
    domain.add_channel(ch_rx1)
    domain.add_channel(ch_rx2)

    ch_tx.busOn()
    ch_rx1.busOn()
    ch_rx2.busOn()

    ch_tx.write(Frame(id_=11, data=b''))
    frame1 = ch_rx1.read(timeout=100)
    frame2 = ch_rx2.read(timeout=100)

    print(f"Timestamps, no reset:   {frame1.timestamp=}, {frame2.timestamp=}")

    domain.add_channel(ch_rx1)
    domain.add_channel(ch_rx2)
    domain.reset_time()

    ch_tx.write(Frame(id_=11, data=b''))
    frame1 = ch_rx1.read(timeout=100)
    frame2 = ch_rx2.read(timeout=100)

    print(f"Timestamps, with reset: {frame1.timestamp=}, {frame2.timestamp=}")


Output:

.. code-block:: bash

    Timestamps, no reset:   frame1.timestamp=75254, frame2.timestamp=72253
    Timestamps, with reset: frame1.timestamp=0, frame2.timestamp=0


Checking MagiSync info
----------------------
Some devices have MagiSync support and channels may end up in MagiSync groups
depending on how their USBs are connected. For grouped channels, the clocks
will run at the same speed. To check grouping and support, `canlib.canlib.TimeDomain.get_data`
can be used. It will return an object of `canlib.canlib.TimeDomainData`.

Printing time domain data:

.. code-block:: python

    from canlib import canlib, Frame

    ch0 = canlib.openChannel(0) # Leaf Light v2
    ch1 = canlib.openChannel(1) # UsbCan pro 2xHS v2
    ch2 = canlib.openChannel(2) # UsbCan pro 2xHS v2

    domain = canlib.TimeDomain()
    domain.add_channel(ch0)
    domain.add_channel(ch1)
    domain.add_channel(ch2)

    data = domain.get_data()
    print(data)

Output:

.. code-block:: bash

    sync_groups: 1, synced_members: 2, non_sync_cards: 1, non_synced_members: 1

In this case, `ch1` and `ch2` were from a device with MagiSync support,
listed under `synced_members`. However, `ch0` did not have MagiSync support
and was therefore listed under `non_synced_members`.
The synced members were connected to the same USB-hub and ended up in the same
MagiSync group. The non-synced member was from a device with only 1 channel.

