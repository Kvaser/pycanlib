import ctypes as ct
from collections import namedtuple

from .. import EAN, VersionNumber
from .address import Address
from .enums import (Accessibility, AddressTypeFlag, Availability, DeviceUsage,
                    ServiceState, StartInfo)
from .exceptions import KvrBlank
from .structures import kvrAddress, kvrDeviceInfo
from .wrapper import dll

# kvrDiscoveryStoreDevices
# kvrDeviceGetServiceStatusText

_ASSUMED_NUMBER_OF_DEFAULT_ADDRESSES = 20


ServiceStatus = namedtuple('ServiceStatus', "state start_info text")


def get_default_discovery_addresses(broadcast=True, stored=False):
    """Retrieve the default discovery addresses

    Args:

        broadcast (`bool`): If ``True`` (the default), then the returned list
            will contain broadcast addresses.

        stored (`bool`): If ``True`` (defaults to ``False``), then the returned
            list will contain earlier stored addresses.

    If both arguments are ``False``, a `ValueError` will be raised.

    Retruns a `list` of `Address` objects.

    """
    num = _ASSUMED_NUMBER_OF_DEFAULT_ADDRESSES
    address_list = (kvrAddress * num)()
    returned_num = ct.c_uint32()

    if broadcast and stored:
        address_type_flags = AddressTypeFlag.ALL
    elif broadcast:
        address_type_flags = AddressTypeFlag.BROADCAST
    elif stored:
        address_type_flags = AddressTypeFlag.STORED
    else:
        raise ValueError('broadcast or stored argument must be True')

    dll.kvrDiscoveryGetDefaultAddresses(
        address_list,
        num,
        ct.byref(returned_num),
        address_type_flags,
    )

    # kvrDiscoveryGetDefaultAddresses doesn't tell us how large address_list
    # needs to be for all answers to fit, so we enlarge it by doubling every
    # time we might have missed some results.
    while num == returned_num.value:
        num *= 2
        address_list = (kvrAddress * num)()
        dll.kvrDiscoveryGetDefaultAddresses(
            address_list,
            num,
            ct.byref(returned_num),
            address_type_flags,
        )

    default_addresses = [Address.from_c(c_addr) for c_addr in address_list[: returned_num.value]]

    return default_addresses


def openDiscovery():
    """Creates and returns a `Discovery` object

    Device discovery is normally done using `discover_info_set`.

    """
    handle = ct.c_int32()
    dll.kvrDiscoveryOpen(ct.byref(handle))
    return Discovery(handle)


def set_clear_stored_devices_on_exit(val):
    """Sets whether kvrlib should clear stored devices when the application exist"""
    dll.kvrDiscoveryClearDevicesAtExit(int(val))


def store_devices(devices):
    """Store a collection of `DeviceInfo` objects in the registry

    See `DeviceInfoSet` for a simpler way of dealing with device
    infos and the registry.

    Note:
        Previously stored devices are cleared.

    """
    DevArray = kvrDeviceInfo * len(devices)
    devarray = DevArray(*(dev.device_info for dev in devices))
    dll.kvrDiscoveryStoreDevices(devarray, len(devarray))


def start_discovery(delay, timeout, addresses=None, report_stored=True):
    """Start and return a `Discovery`

    Device discovery is normally done using `discover_info_set`.

    The returned object should usually be used as a context handler::

        with kvrlib.start_discovery(delay=100, timeout=1000) as disc:
            for result in disc.results():
                # process the discovery result
                print(result)

    """
    disc = openDiscovery()
    if addresses is None:
        addresses = get_default_discovery_addresses()
    disc.addresses = addresses
    disc.start(delay, timeout, report_stored)
    return disc


def stored_devices():
    """Read the devices stored in the registry as a tuple of `DeviceInfo` objects"""
    with start_discovery(0, 0, report_stored=True) as disc:
        stored = tuple(dev for dev in disc.results() if dev.availability & Availability.STORED)

    return stored


class Discovery:
    """A kvrlib "Discovery" process

    Most of the time the discovery process can be handled by
    `.discover_info_set`, which returns the results of the discovery as a
    `.DeviceInfoSet`.

    Even when interacted with directly, instnances of this class are normally
    not instantiated directly, but created using `.start_discovery`, or
    sometimes using `.openDiscovery`.

    Instances of this class can be used as context handlers, in which case the
    discovery will be closed when the context is exited. The discovery will
    also be closed when the instance is garbage collected, if it hasn't
    already.

    """

    def __init__(self, handle):
        self.handle = handle

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    addresses = property(
        doc="""The list of addresses to use for discovery

        Note:
            This attribute is write-only.

        This attribute should be a list of `.Address` objects.

        If the `.Discovery` object was created by `.start_discovery`, the
        addresses are automatically set. Otherwise, they must be assigned
        before `.Discovery.start` can be called.

        """
    )

    @addresses.setter
    def addresses(self, val):
        address_list = (kvrAddress * len(val))(*(a.to_c() for a in val))
        dll.kvrDiscoverySetAddresses(self.handle, address_list, len(val))

    def close(self):
        """Close the discovery process

        This function is called when the `Discovery` object is
        garbage-collected.

        If the `Discovery` object is used as a context handler, this function
        will be called when the context exits.

        """
        if self.handle is not None:
            dll.kvrDiscoveryClose(self.handle)
            self.handle = None

    def results(self):
        """Return an iterator of the result from the discovery

        The results are yielded as `DeviceInfo` objects.
        """
        try:
            while True:
                info = kvrDeviceInfo()
                dll.kvrDiscoveryGetResults(self.handle, ct.byref(info))
                yield DeviceInfo(info)
        except KvrBlank:
            return

    def start(self, delay, timeout, report_stored=True):
        """Run the discovery

        If the `Discovery` object was created by
        `.start_discovery`, the discovery has already been run,
        and this function does not need to be called.

        After the discovery has been run, its results can be retrieved using
        `Discovery.results`.

        Args:

            delay (`int`): The millisecond delay between sending discovery
                messages to addresses in the address list.

            timeout (`int`): The millisecond timeout after all discovery
                messages have been sent, before returning.

            report_stored (`bool`): if ``True`` (the default), stored devices
                will be discovered.

        """
        dll.kvrDiscoveryStartEx(self.handle, delay, timeout, int(report_stored))
        return self


class DeviceInfo:
    """Information about a device that can be written to the registry

    See `.DeviceInfoSet` for information about how to get
    `DeviceInfo` objects, process them, and then write them to the registry.

    """

    def __init__(self, device_info=None):
        if device_info is None:
            device_info = kvrDeviceInfo()
        self.device_info = device_info

    def __repr__(self):
        return '<{cls} {name}({hostname}) - {ean}:{serial}>'.format(
            cls=self.__class__.__name__,
            name=self.name,
            hostname=self.hostname,
            ean=self.ean,
            serial=self.serial,
        )

    @property
    def accessibility(self):
        """`~canlib.kvrlib.Accessibility`: The accessibility of this device"""
        return Accessibility(self.device_info.accessibility)

    @accessibility.setter
    def accessibility(self, val):
        if val not in Accessibility:
            raise TypeError(val + " not a valid Accessibility")
        self.device_info.accessibility = int(val)

    @property
    def availability(self):
        """`~canlib.kvrlib.Availability`: The availability of this device"""
        return Availability(self.device_info.availability)

    @property
    def base_station_id(self):
        """`~canlib.kvrlib.Address`: Address of the base station"""
        return Address.from_c(self.device_info.base_station_id)

    @property
    def client_address(self):
        """`~canlib.kvrlib.Address`: Address of connected client"""
        return Address.from_c(self.device_info.client_address)

    @client_address.setter
    def client_address(self, val):
        if not isinstance(val, Address):
            raise TypeError(str(type(val)) + " received, exptected " + str(Address))
        self.device_info.client_address = val.to_c()

    @property
    def connect(self):
        """`bool`: Whether the service should connect to this device"""
        val = self.device_info.request_connection
        # The attribute can also, secretly, be set to ``3`` to flush dns.
        if val in (0, 1):
            val = bool(val)
        return val

    @connect.setter
    def connect(self, val):
        self.device_info.request_connection = int(val)

    @property
    def device_address(self):
        """`~canlib.kvrlib.Address`: Address of remote device"""
        return Address.from_c(self.device_info.device_address)

    @device_address.setter
    def device_address(self, val):
        if not isinstance(val, Address):
            raise TypeError(str(type(val)) + " received, exptected " + str(Address))
        self.device_info.device_address = val.to_c()

    @property
    def ean(self):
        """`~canlib.ean.EAN`: EAN of device"""
        ean = EAN.from_hilo((self.device_info.ean_hi, self.device_info.ean_lo))
        return ean

    @ean.setter
    def ean(self, val):
        ean = EAN(val)
        self.device_info.ean_hi, self.device_info.ean_lo = ean.hilo()

    @property
    def firmware_version(self):
        """`~canlib.versionnumber.VersionNumber`: Firmware version"""
        version = VersionNumber(
            self.device_info.fw_major_ver,
            self.device_info.fw_minor_ver,
            self.device_info.fw_build_ver,
        )
        return version

    encryption_key = property(
        doc="""`bytes`: The encryption key to use when encrypting communication

        Note:
            This attribute is write-only.

        """
    )

    @encryption_key.setter  # noqa
    def encryption_key(self, val):
        key = ct.create_string_buffer(val)
        dll.kvrDiscoverySetEncryptionKey(self.device_info, key)

    @property
    def hostname(self):
        """`str`: DNS hostname if available, otherwise an empty string"""
        return self.device_info.host_name.decode('utf-8')

    @hostname.setter
    def hostname(self, val):
        self.device_info.host_name = val.encode('utf-8')

    @property
    def name(self):
        """`str`: User-defined name of device"""
        try:
            name = self.device_info.name.decode('utf-8')
        except UnicodeDecodeError:
            name = self.device_info.name.decode('cp1252')
        return name

    @name.setter
    def name(self, val):
        self.device_info.name = val.encode('utf-8')

    password = property(
        doc="""`str`: The accessibility password to use when connecting to a device

        Note:
            This attribute is write-only.

        """
    )

    @password.setter  # noqa
    def password(self, val):
        password = ct.create_string_buffer(val.encode('utf-8'))
        dll.kvrDiscoverySetPassword(self.device_info, password)

    @property
    def serial(self):
        """`int`: The serial number of the device"""
        return self.device_info.ser_no

    @serial.setter
    def serial(self, val):
        if not isinstance(val, int):
            raise TypeError("Serial number must be an int")
        self.device_info.ser_no = val

    @property
    def service_status(self):
        """`~canlib.kvrlib.ServiceStatus`: A tuple with the service status of the device

        The returned tuple has the format ``(state, start_info, text)``, where
        ``state`` is a `.ServiceState`, ``start_info`` is a `.StartInfo`, and
        ``text`` is a `str` with local connection status.

        """
        c_state = ct.c_int32()
        c_start_info = ct.c_int32()
        c_text = ct.create_string_buffer(128)

        dll.kvrDeviceGetServiceStatus(self.device_info, c_state, c_start_info)
        dll.kvrDeviceGetServiceStatusText(self.device_info, c_text, ct.sizeof(c_text))

        # python 2 requires converting from long to int
        state = ServiceState(int(c_state.value))
        start_info = StartInfo(int(c_start_info.value))

        text = c_text.value

        return ServiceStatus(state, start_info, text)

    @property
    def stored(self):
        """`bool`: Whether this `DeviceInfo` was read from the registry"""
        return self.device_info.availability is Availability.STORED

    @property
    def usage(self):
        """`~canlib.kvrlib.DeviceUsage`: Usage status (Free/Remote/USB/Config)"""
        return DeviceUsage(self.device_info.usage)

    def info(self):
        """Create a string with information about the `DeviceInfo`

        To be used when the ``str()`` representation is not detailed enough.

        """
        attrs = (
            'ean',
            'serial',
            'name',
            'hostname',
            'connect',
            'firmware_version',
            'device_address',
            'client_address',
            'base_station_id',
            'usage',
            'accessibility',
            'availability',
        )
        info = '\n'.join(format(attr, '<20') + str(getattr(self, attr)) for attr in attrs)
        return info

    def update(self, other):
        """Update the attributes of this instance

        This function takes a `dict`, and will set the attributes given by the
        keys to the corresponding value (on this object).

        """
        for name, val in other.items():
            setattr(self, name, val)
