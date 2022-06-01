Open Channel
============

Once we have imported `canlib.canlib` to enumerate the connected Kvaser CAN
devices, the next call is likely to be a call to `~canlib.canlib.openChannel`,
which returns a `~canlib.canlib.Channel` object for the specific CAN
circuit. This object is then used for subsequent calls to the library. The
`~canlib.canlib.openChannel` function's first argument is the number of the
desired channel, the second argument is modifier flags `~canlib.canlib.Open`.

`~canlib.canlib.openChannel` may raise several different exceptions, one of
which is `~canlib.canlib.CanNotFound`. This means that the channel specified in
the first parameter was not found, or that the flags passed to
`~canlib.canlib.openChannel` is not applicable to the specified channel.

.. _open_as_can:

Open as CAN
-----------

No special `~canlib.canlib.Open` modifier flag is needed in the flags argument to `~canlib.canlib.openChannel` when opening a channel in CAN mode.

    >>> from canlib import canlib
    >>> canlib.openChannel(channel=0)
    <canlib.canlib.channel.Channel object at 0x0000015B787EDA90>

.. _open_as_can_fd:

Open as CAN FD
--------------

To open a channel in CAN FD mode, either `~canlib.canlib.Open.CAN_FD` or
`~canlib.canlib.Open.CAN_FD_NONISO` needs to be given in the flags argument to
`~canlib.canlib.openChannel`.

This example opens channel 0 in CAN FD mode::

    >>> from canlib import canlib
    >>> ch = canlib.openChannel(
    ...     channel=0,
    ...     flags=canlib.Open.CAN_FD,
    ... )
    >>> ch.close()


Close Channel
-------------

Closing a channel is done using `~canlib.canlib.Channel.close`. If no other
handles are referencing the same CANlib channel, the channel is taken off
bus.

The CAN channel can also be opened and closed using a context manager::

    >>> from canlib import canlib
    >>> with canlib.openChannel(channel=1) as ch:
    ...     ...

.. _check_channel_capabilities:

Check Channel Capabilities
--------------------------
Channel specific information and capabilities are made available by
reading attributes of an instance of type `~canlib.canlib.ChannelData`.

The device clock frequency can be obtained via `~canlib.canlib.ChannelData.clock_info.frequency():`

    >>> from canlib import canlib
    >>> chd = canlib.ChannelData(channel_number=0)
    >>> clock_info = chd.clock_info
    >>> clock_info.frequency()
    80000000

The capabilities of a channel can be obtained by reading attribute `~canlib.canlib.ChannelData.channel_cap`
and `~canlib.canlib.ChannelData.channel_cap_ex`:

    >>> from canlib import canlib
    >>> chd = canlib.ChannelData(channel_number=0)
    >>> chd.channel_cap
    ChannelCap.IO_API|SCRIPT|LOGGER|SINGLE_SHOT|SILENT_MODE|CAN_FD_NONISO|CAN_FD|
    TXACKNOWLEDGE|TXREQUEST|GENERATE_ERROR|ERROR_COUNTERS|BUS_STATISTICS|EXTENDED_CAN
    >>> chd.channel_cap_ex[0]
    ChannelCapEx.BUSPARAMS_TQ

A bitwise AND operator can be used to see if a channel has a specific capability.

    >>> if (chd.channel_cap & canlib.ChannelCap.CAN_FD):
    >>>   print("Channel has support for CAN FD!")
    Channel has support for CAN FD!

The above printouts are just an example, and will differ for different devices and
installed firmware.

.. _set_can_bitrate:

Set CAN Bitrate
---------------

After opening the channel in classic CAN mode (see :ref:`open_as_can`), use `~canlib.canlib.Channel.set_bus_params_tq` to specify the bit timing parameters on the CAN bus.
Bit timing parameters are packaged in an instance of type `~canlib.canlib.busparams.BusParamsTq`.
Note that the synchronization segment is excluded as it is always one time quantum long.

**Example:** Set the bus speed to 500 kbit/s on a CAN device with an 80 MHz oscillator:

    >>> from canlib import canlib
    >>> ch = canlib.openChannel(channel=0)
    >>> params = canlib.busparams.BusParamsTq(
    ...     tq=8,
    ...     phase1=2,
    ...     phase2=2,
    ...     sjw=1,
    ...     prescaler=20,
    ...     prop=3
    ... )
    >>> ch.set_bus_params_tq(params)

In the example a prescaler of 20 is used, resulting in each bit comprising of 160 time quanta (8 * 20).
The nominal bus speed is given by 80 * 10^6 / (20 * 8) = 500 * 10^3.

If uncertain how to set a specific bus speed, one can use `~canlib.canlib.busparams.calc_busparamstq`,
which returns a `~canlib.canlib.busparams.BusParamsTq` object:

    >>> calc_busparamstq(
    ... target_bitrate=470_000,
    ... target_sample_point=82,
    ... target_sync_jump_width=15.3,
    ... clk_freq=clock_info.frequency(),
    ... target_prop_tq=50,
    ... prescaler=2)
    BusParamsTq(tq=85, prop=25, phase1=44, phase2=15, sjw=13, prescaler=2)

For users that are not interested in specifying individual bit timing parameters,
CANlib also provides a set of default parameter settings for the most common
bus speeds through the `~canlib.canlib.Bitrate` class. The predefined
bitrate constants may be set directly in the call to `~canlib.canlib.openChannel`::

    >>> ch = canlib.openChannel(channel=0, bitrate=canlib.Bitrate.BITRATE_500K)

.. list-table:: Bit timing parameters for some of the most common bus speeds on a CAN device with an 80 MHz oscillator [1]_
   :widths: 10 10 10 10 10 10 10 10 10
   :header-rows: 1
   :stub-columns: 1

   * -
     - tq
     - phase1
     - phase2
     - sjw
     - prop
     - prescaler
     - Sample point
     - Bitrate
   * - `~canlib.canlib.Bitrate.BITRATE_10K`
     - 16
     - 4
     - 4
     - 1
     - 7
     - 500
     - 75%
     - 10 kbit/s
   * - `~canlib.canlib.Bitrate.BITRATE_50K`
     - 16
     - 4
     - 4
     - 1
     - 7
     - 100
     - 75%
     - 50 kbit/s
   * - `~canlib.canlib.Bitrate.BITRATE_62K`
     - 16
     - 4
     - 4
     - 1
     - 7
     - 80
     - 75%
     - 62 kbit/s
   * - `~canlib.canlib.Bitrate.BITRATE_83K`
     - 8
     - 2
     - 2
     - 2
     - 3
     - 120
     - 75%
     - 83 kbit/s
   * - `~canlib.canlib.Bitrate.BITRATE_100K`
     - 16
     - 4
     - 4
     - 1
     - 7
     - 50
     - 75%
     - 100 kbit/s
   * - `~canlib.canlib.Bitrate.BITRATE_125K`
     - 16
     - 4
     - 4
     - 1
     - 7
     - 40
     - 75%
     - 125 kbit/s
   * - `~canlib.canlib.Bitrate.BITRATE_250K`
     - 8
     - 2
     - 2
     - 1
     - 3
     - 40
     - 75%
     - 250 kbit/s
   * - `~canlib.canlib.Bitrate.BITRATE_500K`
     - 8
     - 2
     - 2
     - 1
     - 3
     - 20
     - 75%
     - 500 kbit/s
   * - `~canlib.canlib.Bitrate.BITRATE_1M`
     - 8
     - 2
     - 2
     - 1
     - 3
     - 10
     - 75%
     - 1 Mbit/s

If uncertain how to calculate bit timing parameters, appropriate values can be acquired using the
`Bit Timing Calculator <https://www.kvaser.com/support/calculators/can-fd-bit-timing-calculator/>`_.
Note that in classic CAN mode, only the nominal bus parameters are of concern when using the
Bit Timing Calculator.


Set CAN FD Bitrate
------------------

After opening a channel in CAN FD mode (see :ref:`open_as_can_fd`), bit timing parameters
for both the arbitration and data phases need to be set. This is done by a call to
`~canlib.canlib.Channel.set_bus_params_tq`, with two separate instances of type
`~canlib.canlib.busparams.BusParamsTq` as arguments.

**Example:** Set the arbitration phase bitrate to 500 kbit/s and the data phase bitrate to
1000 kbit/s, with sampling points at 80%.

    >>> from canlib import canlib
    >>> ch = canlib.openChannel(channel=0, flags=canlib.Open.CAN_FD)
    >>> params_arbitration = canlib.busparams.BusParamsTq(
    ...     tq=80,
    ...     phase1=16,
    ...     phase2=16,
    ...     sjw=16,
    ...     prescaler=2,
    ...     prop=47
    ... )
    >>> params_data = canlib.busparams.BusParamsTq(
    ...     tq=40,
    ...     phase1=31,
    ...     phase2=8,
    ...     sjw=8,
    ...     prescaler=2,
    ...     prop=0
    ... )
    >>> ch.set_bus_params_tq(params_arbitration, params_data)

For users that are not interested in specifying individual bit timing parameters,
CANlib also provides a set of default parameter settings for the most common
bus speeds through the `~canlib.canlib.BitrateFD` class. The predefined
bitrates may be set directly in the call to `~canlib.canlib.openChannel`::

    >>> ch = canlib.openChannel(
    ...     channel=0,
    ...     flags=canlib.Open.CAN_FD,
    ...     bitrate=canlib.BitrateFD.BITRATE_500K_80P,
    ...     data_bitrate=canlib.BitrateFD.BITRATE_1M_80P,
    ... )

For CAN FD bus speeds other than the predefined `~canlib.canlib.BitrateFD`,
bit timing parameters have to be specified manually.

..
   bit timing parameters have to be specified manually using XXX qqqmac

.. list-table:: Available predefined bitrate constants with corresponding bit timing parameters for a CAN FD device with an 80 MHz oscillator [1]_
   :widths: 5 5 5 5 5 5 5 5 5
   :header-rows: 1
   :stub-columns: 1

   * -
     - tq
     - phase1
     - phase2
     - sjw
     - prop
     - prescaler
     - Sample point
     - Bitrate
   * - `~canlib.canlib.BitrateFD.BITRATE_500K_80P`
     - 40
     - 8
     - 8
     - 8
     - 23
     - 4
     - 80%
     - 500 kbit/s
   * - `~canlib.canlib.BitrateFD.BITRATE_1M_80P`
     - 40
     - 8
     - 8
     - 8
     - 23
     - 2
     - 80%
     - 1 Mbit/s
   * - `~canlib.canlib.BitrateFD.BITRATE_2M_80P`
     - 20
     - 8
     - 4
     - 4
     - 7
     - 2
     - 80%
     - 2 Mbit/s
   * - `~canlib.canlib.BitrateFD.BITRATE_2M_60P`
     - 20
     - 8
     - 8
     - 4
     - 3
     - 2
     - 60%
     - 2 Mbit/s
   * - `~canlib.canlib.BitrateFD.BITRATE_4M_80P`
     - 10
     - 7
     - 2
     - 2
     - 0
     - 2
     - 80%
     - 4 Mbit/s
   * - `~canlib.canlib.BitrateFD.BITRATE_8M_80P`
     - 10
     - 7
     - 2
     - 1
     - 0
     - 1
     - 80%
     - 8 Mbit/s
   * - `~canlib.canlib.BitrateFD.BITRATE_8M_70P`
     - 10
     - 6
     - 3
     - 1
     - 0
     - 1
     - 70%
     - 8 Mbit/s
   * - `~canlib.canlib.BitrateFD.BITRATE_8M_60P`
     - 5
     - 2
     - 2
     - 1
     - 0
     - 2
     - 60%
     - 8 Mbit/s

If uncertain how to calculate bit timing parameters, appropriate values can be acquired using the
`Bit Timing Calculator <https://www.kvaser.com/support/calculators/can-fd-bit-timing-calculator/>`_.

.. _can-driver-modes:

CAN Driver Modes
----------------

Use `~canlib.canlib.Channel.setBusOutputControl` to set the bus driver
mode. This is usually set to `~canlib.canlib.Driver.NORMAL` to obtain the
standard push-pull type of driver. Some controllers also support
`~canlib.canlib.Driver.SILENT` which makes the controller receive only, not
transmit anything, not even ACK bits. This might be handy for e.g. when
listening to a CAN bus without interfering.


    >>> from canlib import canlib
    >>> with canlib.openChannel(channel=1) as ch:
    ...     ch.setBusOutputControl(canlib.Driver.SILENT)
    ...     ...

`~canlib.canlib.Driver.NORMAL` is set by default.

.. note:: Using `~canlib.canlib.Channel.setBusOutputControl` to set the bus
   driver mode to `~canlib.canlib.Driver.SILENT` on a device that do not
   support Silent mode will not result in any error messages or warnings, the
   CAN Driver Mode will just remain in `~canlib.canlib.Driver.NORMAL` mode.

   A device that supports Silent mode returns
   `~canlib.canlib.ChannelCap.SILENT_MODE` when asked using
   `.canlib.ChannelData.channel_cap`.


Legacy Functions
----------------

The following functions are still supported by canlib.


Set CAN Bitrate
_______________

`~canlib.canlib.Channel.setBusParams` can be used to set the CAN bus parameters,
including bitrate, the position of the sampling point etc, they are also described
in most CAN controller data sheets. Depending on device and installed firmware,
the requested parameters may be subject to scaling in order to accommodate device
specific restrictions. As such, reading back bus parameters using
`~canlib.canlib.Channel.getBusParamsFd` can return bus parameter settings different
than the ones supplied. Note however, that a successful call to
`~canlib.canlib.Channel.setBusParamsFd` will always result in the requested bit rate
being set on the bus, along with bus parameters that for all intents and purposes
are equivalent to the ones requested.

Set the speed to 125 kbit/s, each bit comprising 8 (= 1 + 4 + 3) quanta, the
sampling point occurs at 5/8 of a bit; SJW = 1; one sampling point::

   >>> ch.setBusParams(freq=125000, tseg1=4, tseg2=3, sjw=1, noSamp=1)

Set the speed to 111111 kbit/s, the sampling point to 75%, the SJW to 2 and the
number of samples to 1::

   >>> ch.setBusParams(freq=111111, tseg1=5, tseg2=2, sjw=2, noSamp=1)

For full bit timing control, use `~canlib.canlib.Channel.set_bus_params_tq` instead.


Set CAN FD Bitrate
__________________

After a channel has been opened in CAN FD mode, `~canlib.canlib.Channel.setBusParams`,
and `~canlib.canlib.Channel.setBusParamsFd` can be used to set the arbitration
and data phase bitrates respectively. Depending on device and installed firmware,
the requested parameters may be subject to scaling in order to accommodate device
specific restrictions. As such, reading back bus parameters using
`~canlib.canlib.Channel.getBusParamsFd` can return bus parameter settings different
than the ones supplied. Note however, that a successful call to
`~canlib.canlib.Channel.setBusParamsFd` will always result in the requested bit rate
being set on the bus, along with bus parameters that for all intents and purposes
are equivalent to the ones requested.

Set the nominal bitrate to 500 kbit/s and the data phase bitrate to 1000 kbit/s,
with sampling points at 80%.

   >>> ch.setBusParams(freq=500000, tseg1=63, tseg2=16, sjw=16, noSamp=1);
   >>> ch.setBusParamsFd(freq_brs=1000000, tseg1_brs=31, tseg2_brs=8, sjw_brs=8);

For full bit timing control, use `~canlib.canlib.Channel.set_bus_params_tq` instead.

.. [1] See :ref:`check_channel_capabilities` for information on clock frequency.
