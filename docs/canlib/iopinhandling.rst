I/O Pin Handling
================

Initialize
----------

Some Kvaser products feature I/O pins that can be used in real-time
applications using a part of the API dedicated to I/O Pin Handling. This API is
initialized by confirming the I/O pin configuration, see
kvIoConfirmConfig. Before the configuration is confirmed the user can only
retrieve information about the pins.

    >>> from canlib import canlib, Device
    ... device = Device.find(serial=66666)
    ... channel = device.channel_number()
    ... ch = canlib.openChannel(channel)
    ... config = canlib.iopin.Configuration(ch)
    ... ch.get_io_pin(86).pin_type
    <PinType.ANALOG: 2>
    >>> for pin in config:
    ...     print(pin)
    Pin 0: <PinType.DIGITAL: 1> <Direction.OUT: 8> bits=1 range=0.0-24.0 (<ModuleType.DIGITAL: 1>)
    Pin 1: <PinType.DIGITAL: 1> <Direction.OUT: 8> bits=1 range=0.0-24.0 (<ModuleType.DIGITAL: 1>)
     :
    Pin 31: <PinType.DIGITAL: 1> <Direction.IN: 4> bits=1 range=0.0-24.0 HL_filter=5000 LH_filter=5000 (<ModuleType.DIGITAL: 1>)

After the configuration has been confirmed the user may set or read any values
of the I/O pins::

    >>> config.confirm()

    >>> ch.get_io_pin(0).value
    0
    >>> ch.get_io_pin(0).value = 1

    >>> ch.get_io_pin(0).value
    1


Pin Information
---------------

Pins are identified by their pin number, which is a number from zero up to, but
not including, the value returned by `~.canlib.Channel.number_of_io_pins`. Using
the pin number, the specific properties of any pin is retrieved and set using
`.canlib.iopin.IoPin`.


I/O pin types
-------------

There are currently three types of pins that is supported by the API dedicated
to I/O Pin Handling. These include analog, digital and relay pins. To learn
what pin type a given pin is, use `.canlib.iopin.IoPin.pin_type`. See
`~.canlib.iopin.PinType` to see all supported types.


Analog Pins
~~~~~~~~~~~

The analog pins are represented by multiple bits, the number of bits can be
retrieved by calling ~`.canlib.iopin.IoPin.number_of_bits`. The value of an
analog pin is within in the interval given by `~.canlib.iopin.IoPin.range_min`
and `~.canlib.iopin.IoPin.range_min`. The analog input pin has two configurable
properties, namely the low pass filter order and the hysteresis. See
`~.canlib.iopin.AnalogIn.lp_filter_order` and
`~.canlib.iopin.AnalogIn.hysteresis`. Pins are read and set using
`~.canlib.iopin.IoPin.value`. When reading an output, the latest value set is
retrieved.


Digital Pins
~~~~~~~~~~~~

The digital pins have two configurable properties, namely the low-to-high and
the high-to-low filter time. See `~.canlib.iopin.DigitalIn.high_low_filter` and
`~.canlib.iopin.DigitalIn.low_high_filter`. Pins are read and set using
`~.canlib.iopin.IoPin.value`. When reading an output, the latest value set is
retrieved.


Relay Pins
~~~~~~~~~~

The relay pins have no configurable properties. All of these pins are
considered as outputs. Pins are set and read using
`~.canlib.iopin.IoPin.value`.
