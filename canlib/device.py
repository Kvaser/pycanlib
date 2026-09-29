import itertools
import sys
from collections import namedtuple
from importlib import import_module

from . import deprecation


class _Libs:
    """Class to facilitate importing canlib modules on-demand

    The main problem this class solves is that kvrlib is not available on
    linux, so unconditionally importing kvrlib is not an option. However, it is
    also preferable that simply importing this module loads most of pycanlib,
    if a user wants to use `Device` to interact with canlib, they should not
    need to load e.g. kvmlib.

    This class is instanced, once, in device.py as `_libs`. Any time a library,
    for example `canlib`, is used in device.py it will be accessed with
    ``_libs.canlib``. The first time this happens, there will be no ``canlib``
    attribute on ``libs``, and `_Libs.__getattr__` will be called. This looks
    up the library name provided in `_Libs._imports`, which should give a
    no-argument function that imports that library and returns
    it. `_Libs.__getattr__` then saves the returned module as an attribute,
    making sure that `_Libs.__getattr__` is only called the first time any
    particular library is requested.

    """

    def import_kvrlib(self=None):
        try:
            module = import_module('canlib.kvrlib')
        except AttributeError:
            if not sys.platform.startswith('win'):
                raise ImportError("kvrlib is only available on Windows")
            else:
                raise
        else:
            return module

    _imports = {
        'canlib': lambda: import_module('canlib.canlib'),
        'kvmlib': lambda: import_module('canlib.kvmlib'),
        'linlib': lambda: import_module('canlib.linlib'),
        'kvrlib': import_kvrlib,
    }

    def __getattr__(self, name):
        setattr(self, name, self._imports[name]())
        return getattr(self, name)


_libs = _Libs()


_ChannelInfo = namedtuple(
    '_channel_info',
    "channel_number ean serial channel_name",
)
_ChannelInfo.__new__.__defaults__ = tuple(None for _ in _ChannelInfo._fields)


def connected_devices():
    """Get all currently connected devices as `Device`

    Returns an iterator of `Device` object, one object for every physical
    device currently connected.

    .. versionadded:: 1.6

    .. versionchanged:: 1.7
       `Device.last_channel_number` will now be set.


    """
    last_device = None
    for curr_channel in itertools.count():
        try:
            data = _libs.canlib.ChannelData(curr_channel)
            ean = data.card_upc_no
            serial = data.card_serial_no
        except _libs.canlib.CanNotFound:
            return
        except _libs.canlib.exceptions.CanError as e:
            if e.status == _libs.canlib.enums.Error.NOCARD:
                continue
            else:
                raise
        else:
            dev = Device(ean=ean, serial=serial)
            dev.last_channel_number = curr_channel
            if dev != last_device:
                yield dev
                last_device = dev


def _find_channel(info, last=None):
    assert info is not None

    if last is not None:
        try:
            new_info = _match_channel(last, info)
        except _libs.canlib.CanNotFound:
            new_info = None
        if new_info is not None:
            return new_info

    for curr_channel in itertools.count():
        new_info = _match_channel(curr_channel, info)
        if new_info is not None:
            return new_info


def _match_channel(channel_number, info):
    target_ch = info.channel_number
    target_ean = info.ean
    target_serial = info.serial
    target_name = info.channel_name
    if (target_ch is not None) and (channel_number != target_ch):
        return None
    data = _libs.canlib.ChannelData(channel_number)
    ean = data.card_upc_no
    if (target_ean is not None) and (ean != target_ean):
        return None
    serial = data.card_serial_no
    if (target_serial is not None) and (serial != target_serial):
        return None
    name = data.custom_name
    if (target_name is not None) and (name != target_name):
        return None
    chan_no_on_card = data.chan_no_on_card
    # The Device channel_number should always point at the first channel on card
    channel_number -= chan_no_on_card
    return _ChannelInfo(channel_number, ean, serial, name)


class Device:
    """Class for keeping track of a physical device

    This class represents a physical device regardless of whether it is
    currently connected or not, and on which channel it is connected.

    If the device is currently connected, `Device.find` can be used to get a
    `Device` object::

        dev = Device.find(ean=EAN('67890-1'))

    `Device.find` supports searching for devices based on a variety of
    information, and will return a `Device` object corresponding to the first
    physical device that matched its arguments. In this case, it would be the
    first device found with an EAN of 73-30130-67890-1.

    If the device wanted is not currently connected, `Device` objects can be
    created with their EAN and serial number (as this is the minimal
    information needed to uniquely identify a specific device)::

        dev = Device(ean=EAN('67890-1'), serial=42)

    Two `Device` objects can be checked for equality (whether they refer to the same
    device) and be converted to a `str`. `Device.probe_info` can also be used
    for a more verbose string representation that queries the device (if
    connected) for various pieces of information.

    This class also provides functions for creating the other objects of `canlib`:

    * `canlib.Channel` -- `Device.channel`
    * `canlib.ChannelData` -- `Device.channel_data`
    * `canlib.IOControl` -- `Device.iocontrol`
    * `kvmlib.Memorator`-- `Device.memorator`
    * `linlib.Channel` -- `Device.lin_master` and `Device.lin_slave`

    Args:
        ean (`canlib.EAN`): The EAN of this device.
        serial (`int`): The serial number of this device.
        last_channel_number (`int`): The channel number this device was last
            found on (used as an optimization; while the device stays on the
            same CANlib channel there is no need for a linear search of all
            channels).

    .. versionadded:: 1.6

    """

    __slots__ = ("ean", "serial", "last_channel_number")

    @classmethod
    def find(cls, channel_number=None, ean=None, serial=None, channel_name=None):
        """Searches for a specific device

        Goes through all CANlib channels (from zero and up), until one of them
        matches the given arguments. If an argument is omitted or `None`, any
        device will match it. If no devices matches a
        `canlib.CanNotFound` exception will be raised.

        Args:
            channel_number (`int`): Find a device on this CANlib channel (number).
            ean (`canlib.EAN`): Find a device with this EAN.
            serial (`int`): Find a device with this serial number.
            channel_name (`str`): Find a device with this CANlib channel name.

        """
        target_info = _ChannelInfo(channel_number, ean, serial, channel_name)
        info = _find_channel(target_info)
        dev = cls(ean=info.ean, serial=info.serial)
        dev.last_channel_number = info.channel_number  # last known CANlib channel
        return dev

    def __init__(self, ean, serial):
        # setval = super().__setattr__
        # setval("ean", ean)
        # setval("serial", serial)

        # super() is annoying in python 2
        object.__setattr__(self, "ean", ean)
        object.__setattr__(self, "serial", serial)

        # The last channel number this device was found on
        self.last_channel_number = None

    # required in Python 2
    def __ne__(self, other):
        # required in python 2
        eq = self == other
        if eq is NotImplemented:
            return eq
        else:
            return not eq

    def __eq__(self, other):
        if not isinstance(other, Device):
            return NotImplemented

        return self.ean == other.ean and self.serial == other.serial

    def __hash__(self):
        return hash((self.ean, self.serial))

    def __setattr__(self, name, value):
        if name != "last_channel_number":
            raise TypeError(self.__class__.__name__ + " only supports setting last_channel_number")
        else:
            # super().__setattr__(name, value)
            # super() is annoying in python 2
            object.__setattr__(self, name, value)

    def __repr__(self):
        return f"{self.__class__.__name__}(ean={self.ean!r}, serial={self.serial!r})"

    def __str__(self):
        return f"{self.ean}:{self.serial}"

    @deprecation.deprecated.favour(".open_channel()")
    def channel(self, *args, **kwargs):
        """A `~canlib.Channel` for this device's first channel

        The experimental argument `_chan_no_on_card` may be given, the `int`
        provided will be added (without any verifications) to the
        `channel_number` where this device was found on, and may thus be used
        to open a specific local channel on this device.

        NOTE:

            When using the `_chan_no_on_card` attribute, you must make sure
            that the card actually have the assumed number of local channels.
            Using this argument with a too large `int` could return a channel
            belonging to a different device.

        Arguments to `~canlib.openChannel` other than the channel number
        can be passed to this function.

        .. versionchanged:: 1.13
           Added argument `_chan_no_on_card`

        .. deprecated:: 1.16
           Use `open_channel` instead

        """
        _chan_no_on_card = 0
        if '_chan_no_on_card' in kwargs:
            _chan_no_on_card = kwargs.get("_chan_no_on_card")
            del kwargs['_chan_no_on_card']

        # Should we somehow (without affecting performance) check that _chan_no_on_card is small enough?
        channel_number = self.channel_number() + _chan_no_on_card
        return _libs.canlib.openChannel(channel_number, *args, **kwargs)

    def channel_data(self):
        """A `canlib.ChannelData` for this device's first channel"""
        return _libs.canlib.ChannelData(self.channel_number())

    def channel_number(self):
        """An `int` with this device's CANlib channel number"""
        info = _find_channel(
            _ChannelInfo(ean=self.ean, serial=self.serial),
            last=self.last_channel_number,
        )
        self.last_channel_number = info.channel_number
        return info.channel_number

    def iocontrol(self):
        """A `canlib.IOControl` for this device's first channel"""
        return _libs.canlib.IOControl(self.open_channel())

    def isconnected(self):
        """A `bool` whether this device can currently be found"""
        try:
            self.channel_number()
        except _libs.canlib.CanNotFound:
            return False
        else:
            return True

    def issubset(self, other):
        """Check if device is a subset of other Device.

        This can be used to see if a found device fulfills criteria specified
        in other.  Setting an attribute to None is regarded as a Any. This
        means that e.g. any serial number will be a subset of a serial number
        specified as None.

        .. versionadded:: 1.9

        """
        if other.serial is not None and self.serial != other.serial:
            return False
        if other.ean is not None and self.ean != other.ean:
            return False
        return True

    def lin_master(self, *args, **kwargs):
        """A `linlib.Channel` master for this device's first channel

        Arguments to `linlib.openMaster` other than the channel number
        can be passed to this function.

        """
        return _libs.linlib.openMaster(self.channel_number(), *args, **kwargs)

    def lin_slave(self, *args, **kwargs):
        """A `linlib.Channel` slave for this device's first channel

        Arguments to `linlib.openSlave` other than the channel number
        can be passed to this function.

        """
        return _libs.linlib.openSlave(self.channel_number(), *args, **kwargs)

    def memorator(self, *args, **kwargs):
        """A `kvmlib.Memorator` for this device's first channel

        Arguments to `kvmlib.openDevice` other than the channel number
        can be passed to this function.

        """
        return _libs.kvmlib.openDevice(self.channel_number(), *args, **kwargs)

    def open_channel(self, chan_no_on_card=0, **kwargs):
        """A `canlib.Channel` for this device's first channel

        The parameter `chan_no_on_card` will be added (without any
        verifications) to the `channel_number` where this device was found on,
        and may thus be used to open a specific local channel on this device.

        NOTE:

            When using the `chan_no_on_card` parameter, you must make sure
            that the card actually have the assumed number of local channels.
            Using this parameter with a too large `int` could return a channel
            belonging to a different device.

        Arguments to `canlib.open_channel`, other than the channel number,
        can be passed to this function, but must be passed as keyword arguments.

        .. versionadded:: 1.16

        """

        # Should we somehow (without affecting performance) check that
        # chan_no_on_card is small enough?
        channel_number = self.channel_number() + chan_no_on_card
        return _libs.canlib.openChannel(channel=channel_number, **kwargs)

    def probe_info(self):
        """A `str` with information about this device

        This function is useful when the `Device`'s `str()` does not give
        enough information while debugging. When the device is connected
        various pieces of information such as the device name, firmware, and
        driver name is given. When the device is not connected only basic
        information can be given.

        Note:

            Never inspect the return value of this function, only use it for
            displaying information. Exactly what is shown depends on whether
            the device is connected or not, and is not guaranteed to stay
            consistent between versions.

        """
        try:
            data = self.channel_data()
            infos = {
                'CANlib Channel': self.channel_number(),
                'Card Number': data.card_number,
                'Device': data.channel_name,
                'Driver Name': data.driver_name,
                'EAN': self.ean,
                'Firmware': data.card_firmware_rev,
                'Serial Number': self.serial,
            }
        except _libs.canlib.CanNotFound:
            infos = {
                'EAN': self.ean,
                'Last CANlib Channel': self.last_channel_number,
                'Serial Number': self.serial,
            }
        width = max(len(label) for label in infos.keys())
        # We sort the keys before printing as pre python 3.6 the order of
        # dictionary keys is arbitrary, and can change between calls.
        text = '\n'.join(key.ljust(width) + ': ' + str(val) for key, val in sorted(infos.items()))
        return text

    def remote(self, *args, **kwargs):
        """A `kvrlib.RemoteDevice` for this device

        Arguments to `kvrlib.openDevice` other than the channel number
        can be passed to this function.

        """
        return _libs.kvrlib.openDevice(self.channel_number(), *args, **kwargs)
