"""Experimental support for accessing IO-pins on sub modules of the Kvaser DIN
Rail SE 400S and variants that was added to CANlib v5.26.

.. versionadded:: 1.8

"""

import ctypes as ct

from ..cenum import CEnum
from ..versionnumber import VersionNumber
from . import wrapper

dll = wrapper.dll


def get_io_pin(channel, index):
    """Return io pin object for `index`

    Arguments:
        index (`int`): The global pin number

    Returns subclass of `IoPin` depending on pin type and direction:
    `AnalogIn`, `AnalogOut`, `DigitalIn`, `DigitalOut` or `Relay`.

    """
    io_pin = IoPin(channel, index)
    pin_class = _PIN_CLASSES[io_pin.pin_type][io_pin.direction]
    my_io_pin = pin_class(channel, index)
    return my_io_pin


def module_pin_names(module_type, prefix=''):
    """Return a list of names for `module_type`

    Returns a list of label names for the given type of module::

        >>> iopin.module_pin_names(iopin.ModuleType.ANALOG)
        ['AO1', 'AO2', 'AO3', 'AO4', 'AI1', 'AI2', 'AI3', 'AI4']

        >>> iopin.module_pin_names(iopin.ModuleType.RELAY)
        ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'DI1', 'DI2', 'DI3',
        'DI4', 'DI5', 'DI6', 'DI7', 'DI8']

    Args:
        module_type (`iopin.ModuleType`) : Type of module

    """
    if module_type == ModuleType.DIGITAL:
        pin_names = [f'{prefix}DO{x}' for x in range(1, 17)]
        pin_names += [f'{prefix}DI{x}' for x in range(1, 17)]
    elif module_type == ModuleType.ANALOG:
        pin_names = [f'{prefix}AO{x}' for x in range(1, 5)]
        pin_names += [f'{prefix}AI{x}' for x in range(1, 5)]
    elif module_type == ModuleType.RELAY:
        pin_names = [f'{prefix}R{x}' for x in range(1, 9)]
        pin_names += [f'{prefix}DI{x}' for x in range(1, 9)]
    elif module_type == ModuleType.INTERNAL:
        pin_names = ['DO1', 'DI1']
    else:
        raise AttributeError(f"{module_type} is an unknown ModuleType")
    return pin_names


def _create_pin_names(io_pins):
    """Create a list of names for the given list of `iopin.IoPin`.

    Used by `iopin.Configuration` to create a list of label pin names
    from a given list of `iopin.IoPin` s

    """
    module_index = 0
    pin_index = 0
    pin_names = []
    while pin_index < len(io_pins):
        module_index += 1
        names = module_pin_names(io_pins[pin_index].module_type, prefix=f'{module_index}:')
        pin_names += names
        pin_index += len(names)
    return pin_names


class AddonModule:
    """Contains information about one add-on module

    Args:
        module_type (`ModuleType`): The type of the add-on module.
        sw_version (`canlib.VersionNumber`): The software version in the add-on module.
        serial (int): The serial number of the add-on module.
        first_index (int): The index of the add-on modules first pin.

    .. versionadded:: 1.9

    """

    def __init__(self, module_type, fw_version=None, serial=None, first_pin_index=None):
        self.module_type = module_type
        self.fw_version = fw_version
        self.serial = serial
        self.first_pin_index = first_pin_index

    def __repr__(self):
        return "AddonModule(module_type={typ!r}, fw_version={fw!r}, serial={sn}), first_pin_index={fp}".format(
            typ=self.module_type, fw=self.fw_version, sn=self.serial, fp=self.first_pin_index
        )

    def issubset(self, spec):
        """Check if current attributes are fulfilling attributes in *spec*.

        Any attribute in spec that is set to None is automatically considered fulfilled.

        The `fw_version` attribute is considered fulfilled when
        `self.fw_version >= spec.fw_version`.

        This can be used to check if a specific module fulfills a manually
        created specification::

            >>> module_spec = [iopin.AddonModule(module_type=iopin.ModuleType.DIGITAL)]
            ... config = iopin.Configuration(channel)
            >>> config.modules
            [AddonModule(module_type=<ModuleType.DIGITAL: 1>, fw_version=VersionNumber(major=2, minor=5, release=None, build=None), serial=2342), first_pin_index=0]
            >>> config.issubset(module_spec)
            True

            >>> module_spec = [iopin.AddonModule(
                    module_type=iopin.ModuleType.DIGITAL,
                    fw_version=VersionNumber(major=3, minor=1),
                    serial=2342)]

            >>> config.issubset(module_spec)
            False

            >>> module_spec = [
                iopin.AddonModule(module_type=iopin.ModuleType.ANALOG),
                iopin.AddonModule(module_type=iopin.ModuleType.DIGITAL,
                                  fw_version=VersionNumber(major=3, minor=1),
                                  serial=2342)]

            >>> config.issubset(module_spec)
            False

        """
        if spec.module_type is not None and self.module_type != spec.module_type:
            return False
        if spec.fw_version is not None and self.fw_version is None:
            return False
        if spec.fw_version is not None and self.fw_version < spec.fw_version:
            return False
        if spec.serial is not None and self.serial != spec.serial:
            return False
        if spec.first_pin_index is not None and self.first_pin_index != spec.first_pin_index:
            return False
        return True


class Configuration:
    """Contains I/O pins and the `.canlib.Channel` to find them on

    Creating this object may take some time depending on the number of I/O pins
    availably on the given `.canlib.Channel`.

    Args:
        channel (`~.canlib.Channel`): The channel where the discovery of I/O pins
            should take place.

    Attributes:
        io_pins (list(`IoPin`)): All discovered I/O pins.
        modules (list(`AddonModule`)): All included add-on-modules.
        pin_names (list(str)): List of label I/O pin names.
        pin_index (dict(str: int)): Dictionary with I/O pin label name as key, and pin index as value.

    To create an `.iopin.Configuration` you need to supply the `.canlib.Channel`,
    which is were we look for I/O pins:

        >>> from canlib.canlib import iopin
        ... from canlib import canlib, Device, EAN
        ... device = Device.find(ean=EAN('01059-8'), serial=225)
        ... channel = canlib.openChannel(device.channel_number(), canlib.Open.EXCLUSIVE)
        ... config = iopin.Configuration(channel)

    Now we can investigate a specific pin by index::

        >>> config.pin(index=80)
        Pin 80: <PinType.ANALOG: 2> <Direction.OUT: 8> bits=12 range=0.0-10.0 (<ModuleType.ANALOG: 2>)

    It is also possible to find the label name from the index and vice verse
    for a pin, as well as access the pin using the label name::

        >>> config.name(80)
        '4:AO1'

        >>> config.index('4:AO1')
        80

        >>> config.pin(name='4:AO1')
        Pin 80: <PinType.ANALOG: 2> <Direction.OUT: 8> bits=12 range=0.0-10.0 (<ModuleType.ANALOG: 2>)

    Note:
        A configuration needs to be confirmed using `.iopin.Configuration.confirm`
        (which calls `.Channel.io_confirm_config`) before accessing pin values::

            >>> config.pin(name='4:AO1').value = 4
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
              File "...\\canlib\\canlib\\iopin.py", line 271, in value
              File "...\\canlib\\canlib\\dll.py", line 94, in _error_check
                raise can_error(result)
            canlib.canlib.exceptions.IoPinConfigurationNotConfirmed: I/O pin configuration is not confirmed (-45)
            I/O pin configuration is not confirmed (-45)

            >>> config.confirm()

            >>> config.pin(name='4:AO1').value = 4

    A `Configuration` may be compared with an expected ordered list of
    `AddonModule` before confirming using `AddonModule.issubset`

    .. versionchanged:: 1.9
       `Configuration.modules` is now an attribute, containing an ordered list of `AddonModule` objects.

    """

    def __init__(self, channel):
        self._channel = channel
        self.io_pins = []
        for index in range(self._channel.number_of_io_pins()):
            self.io_pins.append(self._channel.get_io_pin(index))
        self.pin_names = _create_pin_names(self.io_pins)
        self.pin_index = {v: i for i, v in enumerate(self.pin_names)}
        self.modules = self._modules()

    def __iter__(self):
        """Returns an iterator for all pins known in configuration"""
        return iter(self.io_pins)

    def _modules(self):
        """Return an up-to-date list of modules in the configuration"""
        modules = []
        pin_index = 0
        while pin_index < len(self.io_pins):
            module = AddonModule(
                module_type=self.io_pins[pin_index].module_type,
                fw_version=self.io_pins[pin_index].fw_version,
                serial=self.io_pins[pin_index].serial,
                first_pin_index=pin_index,
            )
            modules.append(module)
            pin_index += len(module_pin_names(module.module_type))
        return modules

    def confirm(self):
        """Confirm current configuration

        Convenience function that calls `.Channel.io_confirm_config`.

        """
        self._channel.io_confirm_config()

    def index(self, name):
        """Return index for pin with the given label name"""
        return self.pin_index[name]

    def issubset(self, spec):
        """Check if attributes of modules in self is fulfilled by given spec

        This is a convenience method that calls `AddonModule.issubset` on all
        modules given by `self.modules` which can be used to check if the
        current configuration fulfills a manually created specification::

            >>> config = iopin.Configuration(channel)
            >>> config_spec = [iopin.AddonModule(module_type=iopin.ModuleType.ANALOG),
                               iopin.AddonModule(module_type=iopin.ModuleType.DIGITAL,
                                                 fw_version=VersionNumber(major=3, minor=1),
                                                 serial=2342)]

            >>> config.issubset(config_spec)
            False

        .. versionadded:: 1.9

        """
        if len(self.modules) != len(spec):
            return False
        return all((m.issubset(s) for m, s in zip(self.modules, spec)))

    def name(self, index):
        """Return label name for pin with given index"""
        return self.pin_names[index]

    def pin(self, index=None, name=None):
        """Return `IoPin` object using index or name

        Either `index` or `name` must be given, if both are given, the name
        will be used.

        Args:
            index (int): I/O pin index
            name (str): I/O pin name

        """
        if name is not None:
            index = self.pin_index[name]
        return self.io_pins[index]


class Info(CEnum):
    """Enum used internally in `IoPin` for calls to `kvIoPinGetInfo` and `kvIoPinSetInfo`"""

    MODULE_TYPE = 1  #: One of `ModuleType`
    DIRECTION = 2  #: One of `Direction`
    PIN_TYPE = 4  #: One of `PinType`
    NUMBER_OF_BITS = 5  #: Resolution in number of bits. Read-only.
    RANGE_MIN = 6  #: A float that contains the lower range limit in volts. Read-only.
    RANGE_MAX = 7  #: A float that contains the upper range limit in volts. Read-only.
    DI_LOW_HIGH_FILTER = 8
    """Time when a digital input pin goes from HIGH to LOW.

    Filter time in micro seconds when a digital input pin goes from HIGH to LOW.
    Range: 0 - 65000, Default 5000 us

    """
    DI_HIGH_LOW_FILTER = 9
    """Time when a digital input pin goes from LOW to HIGH.

    Filter time in micro seconds when a digital input pin goes from LOW to HIGH.

    Range: 0 - 65000, Default 5000 us
    """
    AI_LP_FILTER_ORDER = 10
    """The low-pass filter order for an analog input pin.

    0 - 16, default 3 (sample time is 1 ms)

    """
    AI_HYSTERESIS = 11
    """The hysteresis in volt.

    The hysteresis in volt for an analog input pin, i.e. the amount the input
    have to change before the sampled value is updated.

    0.0 - 10.0, default 0.3

    """
    MODULE_NUMBER = 14  #: The module number the pin belongs to. The number starts from 0. Read-only.
    SERIAL_NUMBER = 15  #: Serial number of the submodule the pin belongs to. Read-only.
    FW_VERSION = 16  #: Software version number of the submodule the pin belongs to. Read-only.


class ModuleType(CEnum):
    """Enum used for return values in `kvIoPinGetInfo`"""

    DIGITAL = 1  #: Digital Add-on (16 inputs, 16 outputs).
    ANALOG = 2  #: Analog Add-on (4 inputs, 4 outputs).
    RELAY = 3  #: Relay Add-on (8 inputs, 8 outputs).
    INTERNAL = 4  #: Internal Digital module (1 input, 1 output).


class PinType(CEnum):
    """Enum used for values in `Info`"""

    DIGITAL = 1
    ANALOG = 2
    RELAY = 3


class Direction(CEnum):
    """Enum used for values in `Info`"""

    IN = 4  #: Input
    OUT = 8  #: Output


class DigitalValue(CEnum):
    """Enum used digital values"""

    LOW = 0
    HIGH = 1


class IoPin:
    """Base class of I/O ports"""

    def __init__(self, channel, pin):
        self.channel = channel
        self.pin = pin

    def __repr__(self):
        txt = "Pin {p}: {pt!r} {d!r} bits={nb} range={rmin}-{rmax} ({mt!r})".format(
            p=self.pin,
            pt=self.pin_type,
            d=self.direction,
            nb=self.number_of_bits,
            rmin=self.range_min,
            rmax=self.range_max,
            mt=self.module_type,
        )
        return txt

    def _get_info(self, info, buf_type):
        buf = buf_type()
        dll.kvIoPinGetInfo(self.channel.handle, self.pin, info, ct.byref(buf), ct.sizeof(buf))
        return buf.value

    def _set_info(self, info, c_value):
        dll.kvIoPinSetInfo(
            self.channel.handle, self.pin, info, ct.byref(c_value), ct.sizeof(c_value)
        )

    @property
    def fw_version(self):
        """VersionNumber: Firmware version in module (Read-only)"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.FW_VERSION, buf_type)
        fw_version = VersionNumber((value >> 16) & 0xFFFF, value & 0xFFFF)
        return fw_version

    @property
    def direction(self):
        """`Direction`: Pin direction (Read-only)"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.DIRECTION, buf_type)
        return Direction(value)

    @property
    def module_type(self):
        """`ModuleType`: Type of module (Read-only)"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.MODULE_TYPE, buf_type)
        return ModuleType(value)

    @property
    def number_of_bits(self):
        """int: Resolution in number of bits (Read-only)"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.NUMBER_OF_BITS, buf_type)
        return value

    @property
    def pin_type(self):
        """`PinType`: Type of pin (Read-only)"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.PIN_TYPE, buf_type)
        return PinType(value)

    @property
    def range_min(self):
        """float: Lower range limit in volts (Read-only)"""
        buf_type = ct.c_float
        value = self._get_info(Info.RANGE_MIN, buf_type)
        return value

    @property
    def range_max(self):
        """float: Upper range limit in volts (Read-only)"""
        buf_type = ct.c_float
        value = self._get_info(Info.RANGE_MAX, buf_type)
        return value

    @property
    def serial(self):
        """int: Module serial number (Read-only)"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.SERIAL_NUMBER, buf_type)
        return value

    @property
    def value(self):
        """Base class does not implement value attribute"""
        raise AttributeError("can't get attribute value")

    @value.setter
    def value(self, value):
        raise AttributeError("can't set attribute value")

    @property
    def hysteresis(self):
        """Base class does not implement hysteresis attribute"""
        raise AttributeError("can't get attribute hysteresis")

    @hysteresis.setter
    def hysteresis(self, value):
        raise AttributeError("can't set attribute hysteresis")

    @property
    def lp_filter_order(self):
        """Base class does not implement lp_filter_order attribute"""
        raise AttributeError("can't get attribute lp_filter_order")

    @lp_filter_order.setter
    def lp_filter_order(self, value):
        raise AttributeError("can't set attribute lp_filter_order")


class AnalogIn(IoPin):
    def __repr__(self):
        txt = "Pin {p}: {pt!r} {d!r} bits={nb} range={rmin}-{rmax} LP_filter_order={lpfo} hysteresis={h} ({mt!r})".format(
            p=self.pin,
            pt=self.pin_type,
            d=self.direction,
            nb=self.number_of_bits,
            rmin=self.range_min,
            rmax=self.range_max,
            lpfo=self.lp_filter_order,
            h=self.hysteresis,
            mt=self.module_type,
        )
        return txt

    @property
    def hysteresis(self):
        """The hysteresis in Volt for analog input pin"""
        buf_type = ct.c_float
        value = self._get_info(Info.AI_HYSTERESIS, buf_type)
        return value

    @hysteresis.setter
    def hysteresis(self, value):
        c_value = ct.c_float(value)
        self._set_info(Info.AI_HYSTERESIS, c_value)

    @property
    def lp_filter_order(self):
        """The low-pass filter order for analog input pin"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.AI_LP_FILTER_ORDER, buf_type)
        return value

    @lp_filter_order.setter
    def lp_filter_order(self, value):
        c_value = ct.c_uint32(value)
        self._set_info(Info.AI_LP_FILTER_ORDER, c_value)

    @property
    def value(self):
        """Voltage level on the Analog input pin"""
        voltage = ct.c_float()
        dll.kvIoPinGetAnalog(self.channel.handle, self.pin, ct.byref(voltage))
        return voltage.value


class AnalogOut(IoPin):
    @property
    def value(self):
        """Voltage level on the Analog output pin"""
        voltage = ct.c_float()
        dll.kvIoPinGetOutputAnalog(self.channel.handle, self.pin, ct.byref(voltage))
        return voltage.value

    @value.setter
    def value(self, value):
        voltage = ct.c_float(value)
        dll.kvIoPinSetAnalog(self.channel.handle, self.pin, voltage)


class DigitalIn(IoPin):
    def __repr__(self):
        txt = "Pin {p}: {pt!r} {d!r} bits={nb} range={rmin}-{rmax} HL_filter={hlf} LH_filter={lhf} ({mt!r})".format(
            p=self.pin,
            pt=self.pin_type,
            d=self.direction,
            nb=self.number_of_bits,
            rmin=self.range_min,
            rmax=self.range_max,
            lhf=self.low_high_filter,
            hlf=self.high_low_filter,
            mt=self.module_type,
        )
        return txt

    @property
    def high_low_filter(self):
        """Filter time in micro seconds when a digital pin goes from HIGH to LOW"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.DI_HIGH_LOW_FILTER, buf_type)
        return value

    @high_low_filter.setter
    def high_low_filter(self, value):
        c_value = ct.c_uint32(value)
        self._set_info(Info.DI_HIGH_LOW_FILTER, c_value)

    @property
    def low_high_filter(self):
        """Filter time in micro seconds when a digital pin goes from LOW to HIGH"""
        buf_type = ct.c_uint32
        value = self._get_info(Info.DI_LOW_HIGH_FILTER, buf_type)
        return value

    @low_high_filter.setter
    def low_high_filter(self, value):
        c_value = ct.c_uint32(value)
        self._set_info(Info.DI_LOW_HIGH_FILTER, c_value)

    @property
    def value(self):
        """Value on digital input pin (0 or 1)"""
        value = ct.c_uint()
        dll.kvIoPinGetDigital(self.channel.handle, self.pin, ct.byref(value))
        return value.value


class DigitalOut(IoPin):
    @property
    def value(self):
        """Value on digital output pin (0 or 1)"""
        value = ct.c_uint()
        dll.kvIoPinGetOutputDigital(self.channel.handle, self.pin, ct.byref(value))
        return value.value

    @value.setter
    def value(self, value):
        c_value = ct.c_uint(value)
        dll.kvIoPinSetDigital(self.channel.handle, self.pin, c_value)


class Relay(IoPin):
    @property
    def value(self):
        """Value on relay, `0` for off, `1` for on"""
        value = ct.c_uint()
        dll.kvIoPinGetOutputRelay(self.channel.handle, self.pin, ct.byref(value))
        return value.value

    @value.setter
    def value(self, value):
        c_value = ct.c_uint(value)
        dll.kvIoPinSetRelay(self.channel.handle, self.pin, c_value)

    def __repr__(self):
        txt = "Pin {p}: {pt!r} {d!r} bits={nb} ({mt!r})".format(
            p=self.pin,
            pt=self.pin_type,
            d=self.direction,
            nb=self.number_of_bits,
            mt=self.module_type,
        )
        return txt


_PIN_CLASSES = {
    PinType.RELAY: {Direction.IN: Relay, Direction.OUT: Relay},
    PinType.ANALOG: {Direction.IN: AnalogIn, Direction.OUT: AnalogOut},
    PinType.DIGITAL: {Direction.IN: DigitalIn, Direction.OUT: DigitalOut},
}
