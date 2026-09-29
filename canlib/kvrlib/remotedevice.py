import contextlib
import ctypes as ct
import time
from collections import namedtuple

from .address import Address
from .enums import BasicServiceSet, ConfigMode, NetworkState, RegulatoryDomain
from .exceptions import KvrBlank, KvrNoAnswer, KvrPasswordError, KvrUnreachable
from .structures import kvrAddress, kvrCipherInfoElement
from .wrapper import HOST_NAME_MIN_SIZE, dll

AddressInfo = namedtuple('AddressInfo', "address1 address2 netmask gateway is_dhcp")
ConnectionStatus = namedtuple(
    'ConnectionStatus', "state tx_rate rx_rate channel_number rssi tx_power"
)
ConnectionTestResult = namedtuple('ConnectionTestResult', "rssi rtt")
WlanScanResult = namedtuple(
    'WlanScanResult', "rssi channel_number mac bss_type ssid security_text"
)


def openDevice(channel_number, password="", validate_password=False):
    """Create a `RemoteDevice` object bound to a channel number

    Args:
        channel_number (`int`): CANlib channel number of the device to open
        password (`str`): Password of the device, if any
        validate_password (`bool`): Whether the password should be validated
            (defaults to `False`).

    This function checks that a remote-capable device is currently connection
    on the channel `channel_number`. If `validate_password` is ``True``, it
    also checks that the password supplied is correct. If any of these checks
    fail, a `ValueError` will be raised.

    """
    # quickly check that a remote device is connected to this channel number
    try:
        num = ct.c_int32()
        dll.kvrConfigNoProfilesGet(channel_number, ct.byref(num))
    except KvrUnreachable:
        raise ValueError("No remote device on channel " + str(channel_number))

    rdev = RemoteDevice(channel_number, password)

    if validate_password:
        if not rdev.password_valid():
            raise ValueError("Wrong password supplied")

    return rdev


class RemoteDevice:
    """A remote-capable Kvaser device

    This class is normally instantiated with `openDevice`::

        rdev = kvrlib.openDevice(CHANNEL_NUMBER)

    Once this is done, the currently active profile can be accessed::

        active = rdev.active_profile

    All profiles, including the active one, are `ConfigProfile`
    objects, see that documentation for all the operations available for
    profile objects.

    The full list of profiles a device has can be inspected using
    ``rdev.profiles``. This is a `RemoteDevice.ProfileList` object, which works
    much like a list::

        # The profile list can be indexed
        first = rdev.profiles[0]

        # We can check if a configuration belongs to this device with 'in'
        assert first in rdev.profiles

        # The length of the profile list is the number of profiles
        num_profiles = len(rdev.profiles)

        # Using the number of profiles, we can get the last one
        last = rdev.profiles[num_profiles - 1]

        # But negative indexes also work and are a better way of getting
        # the last profile
        last = rdev.profiles[-1]

        # You can also iterate over all profiles
        for profile in rdev.profiles:
            ...

    `RemoteDevice` also lets you access a variety of information about the
    specific device, as well as the ability to do a WLAN scan with
    `RemoteDevice.wlan_scan`.

    If the device is password protected, that password can be passed to
    `openDevice`::

        protected_device = kvrlib.openDevice(0, password="Once upon a playground rainy")

    After the object is created, the password is available as::

        password = protected_device.password

    The password can be changed with::

        protected_device.password = "Wolves without teeth"

    The reason the password is stored as clear-text is because it must be
    supplied to the underlying library each time an operation is done using
    this and related classes. This also means that the password is only
    validated, and required, when one of the functions requiring a password is
    called.

    If the device is not password-protected, the password should be an empty string::

        unprotected_device = kvrlib.openDevice(1)
        assert unprotected_device.password == ''

    """

    class ProfileList:
        """The available profiles in a remote-capable device

        This is the type of `RemoteDevice.profiles`. It implements the following:

        * ``len(profiles)``
        * ``profile in profiles``
        * ``profile[index]``

        """

        def __init__(self, channel_number):
            self.channel_number = channel_number

        def __len__(self):
            num = ct.c_int32()
            dll.kvrConfigNoProfilesGet(self.channel_number, ct.byref(num))
            return num.value

        def __contains__(self, profile):
            if not isinstance(profile, ConfigProfile):
                return False
            elif profile.channel_number != self.channel_number:
                # Multichannel devices must use same CANlib channel
                return False
            else:
                return 0 <= profile.profile_number < len(self)

        def __getitem__(self, index):
            if index < 0:
                index = len(self) + index
            profile = ConfigProfile(self, index)
            if profile not in self:
                raise KeyError(index)
            else:
                return profile

    def __init__(self, channel_number, password):
        self.channel_number = channel_number
        self.password = password
        self.profiles = self.ProfileList(self.channel_number)

    @property
    def active_profile(self):
        """`ConfigProfile`: The currently active profile

        Activating another profile is done by assigning this attribute to
        another profile::

            new_profile = remote_device.profiles[index]
            remote_device.active_profile = new_profile

        The value assigned to this property must be a
        `ConfigProfile` that belongs to this device, i.e. the
        following must be ``True``::

            new_profile in remote_device.profiles

        """
        profile_number = ct.c_int32()
        dll.kvrConfigActiveProfileGet(self.channel_number, profile_number)
        return ConfigProfile(self, profile_number.value)

    @active_profile.setter
    def active_profile(self, val):
        # pause required
        if not isinstance(val, ConfigProfile):
            raise TypeError("active_profile must be a kvrlib.ConfigProfile object")
        elif val not in self.profiles:
            raise ValueError("active_profile must be a profile of this device")

        dll.kvrConfigActiveProfileSet(self.channel_number, val.profile_number)

    @property
    def address_info(self):
        """`AddressInfo`: Information about network address settings

        Note:
            Accessing this attribute requires the correct password be set on the object.

        """
        address1 = kvrAddress()
        address2 = kvrAddress()
        netmask = kvrAddress()
        gateway = kvrAddress()
        dhcp = ct.c_int32()

        with self._config_handle(self.password) as handle:
            dll.kvrNetworkGetAddressInfo(
                handle,
                ct.byref(address1),
                ct.byref(address2),
                ct.byref(netmask),
                ct.byref(gateway),
                ct.byref(dhcp),
            )

        address1 = Address.from_c(address1)
        address2 = Address.from_c(address2)
        netmask = Address.from_c(netmask)
        gateway = Address.from_c(gateway)
        dhcp = bool(dhcp)

        return AddressInfo(address1, address2, netmask, gateway, dhcp)

    @property
    def connection_status(self):
        """`ConnectionStatus`: Connection status information

        The returned tuple is a ``(state, tx_rate, rx_rate, channel, rssi,
        tx_power)`` namedtuple of:

        #. ``state`` (`NetworkState`): Network connection state
        #. ``tx_rate`` (`int`): Transmit rate in kbit/s
        #. ``rx_rate`` (`int`): Receive rate in kbit/s
        #. ``channel`` (`int`): Channel
        #. ``rssi`` (`int`): Receive Signal Strength Indicator
        #. ``tx_power`` (`int`): Transmit power level in dB

        Note:
            Accessing this attribute requires the correct password be set on the object.

        """
        state = ct.c_int32()
        tx_rate = ct.c_int32()
        rx_rate = ct.c_int32()
        channel = ct.c_int32()
        rssi = ct.c_int32()
        tx_power = ct.c_int32()

        with self._config_handle(self.password) as handle:
            dll.kvrNetworkGetConnectionStatus(
                handle,
                ct.byref(state),
                ct.byref(tx_rate),
                ct.byref(rx_rate),
                ct.byref(channel),
                ct.byref(rssi),
                ct.byref(tx_power),
            )

        state = NetworkState(state.value)
        tx_rate = tx_rate.value
        rx_rate = rx_rate.value
        channel = channel.value
        rssi = rssi.value
        tx_power = tx_power.value

        return ConnectionStatus(state, tx_rate, rx_rate, channel, rssi, tx_power)

    @property
    def hostname(self):
        """`str`: Device's hostname

        Note:
            Accessing this attribute requires the correct password be set on the object.

        """
        buf = ct.create_string_buffer(HOST_NAME_MIN_SIZE)
        with self._config_handle(self.password) as handle:
            dll.kvrNetworkGetHostName(
                handle,
                buf,
                ct.sizeof(buf),
            )
        return buf.value.decode('utf-8')

    def connection_test(self):
        """Creates a connection test for this device

        Returns:
            `ConnectionTest`

        See the documentation of `ConnectionTest` for more
        information.

        Note:
            Accessing this attribute requires the correct password be set on the object.

        """
        handle = self._loose_config_handle(self.password)
        return ConnectionTest(handle)

    def password_valid(self):
        """Checks whether the password set is valid

        Returns:
            `bool`: ``True`` if the password is valid, ``False`` otherwise.

        """
        try:
            handle = self._loose_config_handle(self.password)
        except KvrPasswordError:
            return False
        else:
            dll.kvrConfigClose(handle)
            return True

    def wlan_scan(self, active=False, bss_type=BasicServiceSet.ANY, domain=RegulatoryDomain.WORLD):
        """Creates and starts a wlan scan for this device

        Returns:
            `WlanScan`

        See the documentation of `WlanScan` for more
        information.

        Note:
            Accessing this attribute requires the correct password be set on the object.

        """
        handle = self._loose_config_handle(self.password)
        scan = WlanScan(handle)
        scan._start(active, bss_type, domain)
        return scan

    def _loose_config_handle(self, password):
        password = ct.create_string_buffer(password.encode('utf-8'))
        handle = ct.c_int32()
        dll.kvrConfigOpen(self.channel_number, ConfigMode.R, password, handle)
        return handle

    @contextlib.contextmanager
    def _config_handle(self, password):
        handle = self._loose_config_handle(password)

        yield handle

        dll.kvrConfigClose(handle)


class ConfigProfile:
    """A configuration profile of a remote-capable device

    The active profile for a `RemoteDevice`, ``rdev``, is accessed with::

        profile = rdev.active_profile

    Other profiles are accessed with ``profiles``::

        first = rdev.profiles[0]

    See the documentation for `RemoteDevice` for more information
    on how to get `ConfigProfile` objects.

    The specific configuration of a profile can be read::

        xml_string = profile.read()

    And it can also be written back::

        profile.write(xml_string)

    The password used by this object is taken from its parent `RemoteDevice`
    object. See that documentation for how to set the password.

    """

    XML_BUFFER_SIZE = 2046

    def __init__(self, device, profile_number):
        self._device = device
        self.profile_number = profile_number

    def __repr__(self):
        return "<ConfigProfile number {pn} of device on CANlib channel {cn}>".format(
            pn=self.profile_number, cn=self.channel_number
        )

    @property
    def channel_number(self):
        """`int`: The CANlib channel number used to communicate with the device"""
        return self._device.channel_number

    @property
    def info(self):
        """`str`: A simplified version of the configuration

        It is not necessary to know the configuration password to access this
        information. Note that the partial XML data returned is not enough to
        reconfigure a device.

        """
        xml_buffer = ct.create_string_buffer(self.XML_BUFFER_SIZE)

        try:
            dll.kvrConfigInfoGet(
                self.channel_number, self.profile_number, xml_buffer, ct.sizeof(xml_buffer)
            )
        except KvrBlank:
            xml = None
        else:
            xml = xml_buffer.value.decode('utf-8')

        return xml

    @property
    def password(self):
        """`str`: The password used to communicate with the device"""
        return self._device.password

    def clear(self):
        """Clear the configuration

        This will also clear any previously set device password.

        Note:
            This method requires the parent `RemoteDevice` to have the correct password.

        """
        # pause required
        with self._open(self.password, ConfigMode.ERASE) as handle:
            dll.kvrConfigClear(handle)

    def read(self):
        """Read the configuration

        Returns either an XML string, or `None` if there is no configuration.

        Note that `ConfigProfile.write` can handle `None`; in other words::

            xml = profile.read()

            # Do anything, including writing new configurations
            ...

            profile.write(xml)

        Will always work even if ``xml`` is `None`. This would mean that the
        profile originally had an empty configuration, and it will once again
        have an empty configuration at the end.

        Note:
            This method requires the parent `RemoteDevice` to have the correct password.

        """
        xml_buf = ct.create_string_buffer(self.XML_BUFFER_SIZE)

        with self._open(self.password, ConfigMode.R) as handle:
            try:
                dll.kvrConfigGet(handle, xml_buf, ct.sizeof(xml_buf))
            except KvrBlank:
                pass
        try:
            xml_text = xml_buf.value.decode('utf-8')
        except UnicodeDecodeError:
            xml_text = xml_buf.value.decode('cp1252')
        return xml_text or None

    def write(self, xml):
        """Write the configuration area

        This function takes as its single argument either an xml string that
        will be written to this profile, or `None` in which case the
        configuration will be cleared.

        Note:
            This method requires the parent `RemoteDevice` to have the correct password.

        """
        if xml is None:
            self.clear()
        else:
            xml_buf = ct.create_string_buffer(xml.encode('utf-8'))
            with self._open(self.password, ConfigMode.RW) as handle:
                dll.kvrConfigSet(handle, xml_buf)

    @contextlib.contextmanager
    def _open(self, password, mode):
        password = ct.create_string_buffer(password.encode('utf-8'))
        handle = ct.c_int32()
        dll.kvrConfigOpenEx(
            self.channel_number,
            mode,
            password,
            ct.byref(handle),
            self.profile_number,
        )

        yield handle

        dll.kvrConfigClose(handle)


class ConnectionTest:
    """A connection test for a specific device

    A connection test for a `RemoteDevice`, ``rdev``, is created by::

        test = rdev.connection_test()

    While a connection test is running, the device will connect and start
    pinging itself to measure round-trip time (RTT) and Receive Signal Strength
    Indicator (RSSI).

    A `ConnectionTest` is started with `ConnectionTest.start` and stopped with
    `ConnectionTest.stop`, after which its results are retrieved by
    `ConnectionTest.results`. If it is acceptable to block while the test is
    running, these three calls can be combined into `ConnectionTest.run`::

        results = test.run(duration=10)
        print(results)

    Connection tests are automatically closed when garbage-collected, but they
    can also be closed manually with `ConnectionTest.close`.

    """

    def __init__(self, config_handle):
        self._handle = config_handle

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the internal handle"""
        if self._handle is not None:
            dll.kvrConfigClose(self._handle)
            self._handle = None

    def results(self, maxresults=20):
        """Get the results from a connection test

        The test must have been running for any results to be available.

        This function returns a `ConnectionTestResult`, which is a namedtuple
        of ``(rssi, rtt)``. Both ``rssi`` and ``rtt`` are tuples containing a
        number of individual results for RSSI and RTT.

        Args:

            maxresults (`int`): The maximum number of rssi and rtt numbers to
                return. The returned ``rssi`` and ``rtt`` will be tuples with
                this long or the number of results available long, whichever is
                shortest.

        """
        rssi_size = maxresults
        rssi = (ct.c_int32 * rssi_size)()
        rssi_count = ct.c_uint32()
        rtt_size = maxresults
        rtt = (ct.c_uint32 * rtt_size)()
        rtt_count = ct.c_uint32()

        dll.kvrNetworkGetRssiRtt(
            self._handle,
            rssi,
            len(rssi),
            ct.byref(rssi_count),
            rtt,
            len(rtt),
            ct.byref(rtt_count),
        )

        rssi = rssi[: rssi_count.value]
        rtt = rtt[: rtt_count.value]
        return ConnectionTestResult(tuple(rssi), tuple(rtt))

    def run(self, duration, maxresults=20):
        """Run a connection test and return its results.

        This function calls `ConnectionTest.start`, then blocks for `duration`
        seconds, then calls `ConnectionTest.stop` before finally returning the
        `ConnectionTestResult` from `ConnectionTest.results`.

        Args:
            duration (`int`): Seconds to run the test for.
            maxresults (`int`): Passed to `ConnectionTest.results` as ``maxlen``.

        """
        self.start()
        time.sleep(duration)
        self.stop()
        return self.results(maxresults)

    def start(self):
        """Start the connection test"""
        dll.kvrNetworkConnectionTest(self._handle, 1)

    def stop(self):
        """Stop the connection test"""
        dll.kvrNetworkConnectionTest(self._handle, 0)


class WlanScan:
    """A wlan scan for this device

    The device starts scanning as soon as this object is created by `RemoteDevice.wlan_scan`::

        scan = rdev.wlan_scan()

    When calling `RemoteDevice.wlan_scan`, you can also specify whether the
    scan should be an active one, the Basic Service Set (bss) to use, and the
    regulatory domain::

        scan = rdev.wlan_scan(
            active=True,
            bss=kvrlib.BasicServiceSet.INFRASTRUCTURE,
            domain=kvrlib.RegulatoryDomain.EUROPE_ETSI,
        )

    Results from the scan are retrieved by iterating over the `WlanScan` object:

        for result in scan:
            print(result)

    When getting the next result, the code will block until a new result is
    available or until no more results are available, in which case the
    iteration stops.

    Wlan scans are automatically closed when garbage-collected, but they
    can also be closed manually with `WlanScan.close`.

    """

    def __init__(self, config_handle):
        self._handle = config_handle

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def __iter__(self):
        try:
            while True:
                try:
                    yield self._get_result()
                except KvrNoAnswer:
                    # "waiting for further scan results"
                    time.sleep(0.1)
        except KvrBlank:
            # "no further scan results are available"
            return

    def close(self):
        """Closes the internal handle"""
        if self._handle is not None:
            dll.kvrConfigClose(self._handle)
            self._handle = None

    def _get_result(self):
        rssi = ct.c_int32()
        channel = ct.c_int32()
        mac = kvrAddress()
        bss_type = ct.c_int32()
        ssid = ct.create_string_buffer(32)
        capability = ct.c_uint32()
        type_wpa = ct.c_uint32()
        wpa_info = kvrCipherInfoElement()
        rsn_info = kvrCipherInfoElement()

        dll.kvrWlanGetScanResults(
            self._handle,
            ct.byref(rssi),
            ct.byref(channel),
            ct.byref(mac),
            ct.byref(bss_type),
            ssid,
            ct.byref(capability),
            ct.byref(type_wpa),
            ct.byref(wpa_info),
            ct.byref(rsn_info),
        )

        security_text = ct.create_string_buffer(180)
        dll.kvrWlanGetSecurityText(
            security_text,
            ct.sizeof(security_text),
            capability,
            type_wpa,
            wpa_info,
            rsn_info,
        )

        return WlanScanResult(
            rssi.value,
            channel.value,
            Address.from_c(mac),
            BasicServiceSet(bss_type.value),
            ssid.value,
            security_text.value,
        )

    def _start(self, active, bss_type, domain):
        dll.kvrWlanStartScan(
            self._handle,
            active,
            bss_type,
            domain,
        )
