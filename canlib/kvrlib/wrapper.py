import ctypes as ct
import logging
import re
import sys
from collections import namedtuple
from xml.dom import minidom

from .. import VersionNumber, deprecation, dllLoader
from . import constants as const
from .dll import KvrlibDll
from .enums import Error
from .exceptions import KvrBlank
from .structures import (kvrAddress, kvrAddressList, kvrDeviceInfo,
                         kvrDeviceInfoList)

_ct_dll = dllLoader.load_dll(win_name='kvrlib.dll')
dll = KvrlibDll(_ct_dll)
dll.kvrInitializeLibrary()

HOST_NAME_MIN_SIZE = 26
CONFIG_VERIFICATION_SIZE = 2048


WEPKeys = namedtuple('WEPKeys', "key64 key128")


def generate_wep_keys(pass_phrase):
    """Generates four 64-bit and one 128-bit WEP keys

    Args:
        pass_phrase (`str`): The pass phrase to use to generate the keys.

    Returns a ``(key64, key128)`` (`WEPKeys`) namedtuple, where ``key64`` is a
    list of four `bytes` object with the four 64-bit WEP keys, and where
    ```key128`` is a `bytes` object with the single 128-bit WEP key.

    """
    phrase = ct.create_string_buffer(pass_phrase.encode('utf-8'))
    key64_1 = ct.create_string_buffer(11)
    key64_2 = ct.create_string_buffer(11)
    key64_3 = ct.create_string_buffer(11)
    key64_4 = ct.create_string_buffer(11)
    key128 = ct.create_string_buffer(27)
    dll.kvrNetworkGenerateWepKeys(
        phrase,
        key64_1,
        key64_2,
        key64_3,
        key64_4,
        key128,
    )
    key64 = (key64_1.value, key64_2.value, key64_3.value, key64_4.value)
    keys = WEPKeys(key64, key128.value)
    print(keys)
    return keys


def generate_wpa_keys(pass_phrase, ssid):
    """Generate a WPA key from a pass phrase and ssid

    Args:
        pass_phrase (`str`): The pass phrase to use to generate the key.
        ssid (`str`): The SSID to use to generate the key.

    Returns:
        `bytes`: The generated WPA key.

    """
    phrase = ct.create_string_buffer(pass_phrase.encode('utf-8'))
    ssid = ct.create_string_buffer(ssid.encode('utf-8'))
    key = ct.create_string_buffer(65)
    dll.kvrNetworkGenerateWpaKeys(
        phrase,
        ssid,
        key,
    )
    return key.value


def hostname(ean, serial):
    """Generate a hostname from ean and serial number

    Args:
        ean (`.canlib.EAN`): European Article Number
        serial (`int`): Serial number

    """
    buf = ct.create_string_buffer(HOST_NAME_MIN_SIZE)
    hi, lo = ean.hilo()
    dll.kvrHostName(hi, lo, serial, buf, ct.sizeof(buf))
    return buf.value.decode('utf-8')


def verify_xml(xml_string):
    """Verify that the xml string complies with both the DTD and internal restrictions"""
    xml = ct.create_string_buffer(xml_string.encode('utf-8'))
    err = ct.create_string_buffer(CONFIG_VERIFICATION_SIZE)

    status = dll.kvrConfigVerifyXml(xml, err, ct.sizeof(err))
    error_string = err.value.decode('utf-8')
    if status == Error.BUFFER_TOO_SMALL:
        error_string += '...(string was truncated)'
    return error_string


class kvrConfig:
    MODE_R = 0
    MODE_RW = 1
    MODE_ERASE = 2

    XML_BUFFER_SIZE = 2046

    def __init__(self, kvrlib=None, channel=0, mode=MODE_R, password="", profile_no=0):
        """parameter kvrlib is deprecated"""
        self.channel = channel
        self.mode = mode
        self.password = password.encode()
        self.profile_no = profile_no
        self.handle = None
        self.openEx()

    def _open(self):
        assert self.handle is None, "previous handle was not closed"
        if self.handle is None:
            self.handle = ct.c_int32(-1)
        dll.kvrConfigOpen(self.channel, self.mode, self.password, ct.byref(self.handle))

    def openEx(self, channel=None, mode=None, password=None, profile_no=None):
        assert self.handle is None, "previous handle was not closed"
        if self.handle is None:
            self.handle = ct.c_int32(-1)
        if channel is not None:
            self.channel = channel
        if mode is not None:
            self.mode = mode
        if password is not None:
            self.password = password
        if profile_no is not None:
            self.profile_no = profile_no
        dll.kvrConfigOpenEx(
            self.channel, self.mode, self.password, ct.byref(self.handle), self.profile_no
        )

    def close(self):
        dll.kvrConfigClose(self.handle)
        self.handle = None

    def getXml(self):
        if self.handle is None:
            self._open()
        xml_buffer = ct.create_string_buffer(self.XML_BUFFER_SIZE)
        dll.kvrConfigGet(self.handle, xml_buffer, self.XML_BUFFER_SIZE)
        self.xml = minidom.parseString(xml_buffer.value)
        return self.xml

    def setXml(self):
        if self.handle is None:
            self._open()
        dll.kvrConfigSet(self.handle, self.xml.toxml().encode('utf-8'))

    def clear(self):
        dll.kvrConfigClear(self.handle)


class kvrDiscovery:
    def __init__(self, kvrlib=None):
        """parameter kvrlib is deprecated"""
        self.handle = ct.c_int32(0xFF)
        dll.kvrDiscoveryOpen(ct.byref(self.handle))
        self.delay_ms = 100
        self.timeout_ms = 1000

    @classmethod
    def getDefaultAddresses(cls, addressTypeFlag=const.kvrAddressTypeFlag_BROADCAST, listSize=20):

        address_list = kvrAddressList(listSize)
        address_list_count = ct.c_uint32(listSize)
        dll.kvrDiscoveryGetDefaultAddresses(
            address_list.STRUCT_ARRAY,
            address_list.elements,
            ct.byref(address_list_count),
            addressTypeFlag,
        )
        address_list.count = address_list_count.value
        return address_list

    def close(self):
        dll.kvrDiscoveryClose(self.handle)

    # qqqmac not using handle - should this be classmethod?
    def clearDevicesAtExit(self, onoff):
        dll.kvrDiscoveryClearDevicesAtExit(onoff)

    def setAddresses(self, addressList):
        dll.kvrDiscoverySetAddresses(self.handle, addressList.STRUCT_ARRAY, addressList.count)

    # qqqmac not using handle - a different object or classmethod?
    def setEncryptionKey(self, device_info, key):
        dll.kvrDiscoverySetEncryptionKey(device_info, key)

    # qqqmac not using handle - a different object or classmethod?
    def setPassword(self, device_info, password):
        dll.kvrDiscoverySetPassword(device_info, password)

    def setScanTime(self, delay_ms, timeout_ms):
        self.delay_ms = delay_ms
        self.timeout_ms = timeout_ms

    def start(self, delay_ms=None, timeout_ms=None):
        if delay_ms is not None:
            self.delay_ms = delay_ms
        if timeout_ms is not None:
            self.timeout_ms = timeout_ms
        dll.kvrDiscoveryStart(self.handle, self.delay_ms, self.timeout_ms)

    # qqqmac not using handle - a different object or classmethod?
    def storeDevices(self, deviceInfos):
        deviceInfoList = kvrDeviceInfoList(deviceInfos)
        dll.kvrDiscoveryStoreDevices(deviceInfoList.STRUCT_ARRAY, deviceInfoList.elements)

    def getResults(self):
        self.start()
        deviceInfoList = []
        while True:
            try:
                deviceInfo = kvrDeviceInfo()
                dll.kvrDiscoveryGetResults(self.handle, deviceInfo)
                deviceInfoList.append(deviceInfo)
            except (KvrBlank):
                break
        return deviceInfoList


def initializeLibrary():
    dll.kvrInitializeLibrary()


def ean2ean_hi(ean):
    """Return EAN high part.

    Returns the high part of the supplied EAN as an integer.
    Calling ean2ean_hi(ean="73-30130-00671-3") returns 0x73301.
    """
    eanCompact = re.sub('-', '', ean)
    match = re.match(r'(\d{5})(\d{8})', eanCompact)
    return int(f'0x{match.group(1)}', 0)


def ean2ean_lo(ean):
    """Return EAN low part.

    Returns the low part of the supplied EAN as an integer.
    Calling ean2ean_lo(ean="73-30130-00671-3") returns 0x30006713.
    """
    eanCompact = re.sub('-', '', ean)
    match = re.match(r'(\d{5})(\d{8})', eanCompact)
    return int(f'0x{match.group(2)}', 0)


def ean_hi_lo2ean(ean_hi, ean_lo):
    """Build EAN from high and low part.

    Returns the EAN as a string built from high and low parts in integer
    format.  Calling ean_hi_lo2ean(ean_hi=0x73301, ean_lo=0x30006713)
    returns "73-30130-00671-3".
    """
    return "{:02x}-{:05x}-{:05x}-{:x}".format(
        ean_hi >> 12,
        ((ean_hi & 0xFFF) << 8) | (ean_lo >> 24),
        (ean_lo >> 4) & 0xFFFFF,
        ean_lo & 0xF,
    )


def deviceGetServiceStatus(device_info):
    """Returns local connection status of the selected device."""
    state = ct.c_int32(-1)
    start_info = ct.c_int32(-1)
    dll.kvrDeviceGetServiceStatus(ct.byref(device_info), ct.byref(state), ct.byref(start_info))
    return (state.value, start_info.value)


def deviceGetServiceStatusText(device_info):
    """Returns local connection status of the selected device as ASCII text."""
    msg = ct.create_string_buffer(80)
    dll.kvrDeviceGetServiceStatusText(ct.byref(device_info), msg, ct.sizeof(msg))
    return msg.value.decode('utf-8')


def addressFromString(type, address):
    kvaddr = kvrAddress()
    dll.kvrAddressFromString(type, kvaddr, address.encode('utf-8'))
    return kvaddr


def stringFromAddress(address):
    addr = ct.create_string_buffer(80)
    dll.kvrStringFromAddress(addr, ct.sizeof(addr), address)
    return addr.value.decode('utf-8')


def configActiveProfileSet(channel, profile_number):
    """Set active profile."""
    dll.kvrConfigActiveProfileSet(channel, profile_number)


def configActiveProfileGet(channel):
    """Get active profile."""
    no_profiles = ct.c_int32(-1)
    dll.kvrConfigActiveProfileGet(channel, ct.byref(no_profiles))
    return no_profiles.value


def configNoProfilesGet(channel):
    """Get the maximum number of profile(s) the device can store.

    When a remote device is connected to the host it can be configured. The
    remote device can hold a number of different profiles.

    """
    no_profiles = ct.c_int32(-1)
    dll.kvrConfigNoProfilesGet(channel, ct.byref(no_profiles))
    return no_profiles.value


def unload():
    """Unloads library stuff."""
    dll.kvrUnloadLibrary()


@deprecation.deprecated.favour('dllversion')
def getVersion():
    """Get the kvrlib version number as a `str`

    .. deprecated:: 1.5
       Use `dllversion` instead.

    """
    return str(dllversion())


def dllversion():
    """Get the kvrlib version number as a `~canlib.VersionNumber`"""
    v = dll.kvrGetVersion()
    return VersionNumber(v.major, v.minor)


# For backwards compatibility
def discoveryOpen():
    return kvrDiscovery(sys.modules[__name__])


# For backwards compatibility
def configOpen(channel=0, mode=kvrConfig.MODE_R):
    return kvrConfig(channel=channel, mode=mode)


class KvrLib:
    """Deprecated wrapper class for the Kvaser kvrlib.

    .. deprecated:: 1.5

    All functionality of this class has been moved to the kvrlib module itself::

      # deprecated
      from canlib import kvrlib
      cl = kvrlib.KvrLib()  # or kvrlib.Kvrlib()
      cl.functionName()

      # use this instead
      from canlib import kvrlib
      kvrlib.functionName()

    """

    dll = dll

    # ean:    73-30130-00671-3
    # ean_hi: 0x73301
    # ean_lo: 0x30006713
    def __init__(self, debug=None):
        fmt = '[%(levelname)s] %(funcName)s: %(message)s'
        if debug:
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=fmt)
        else:
            logging.basicConfig(stream=sys.stderr, level=logging.ERROR, format=fmt)

        deprecation.manual_warn(
            "Creating KvrLib objects is deprecated, "
            "all functionality has been moved to the kvrlib module itself."
        )
        # since=1.5
        self._module = sys.modules[__name__]
        dll.kvrInitializeLibrary()

    def __getattr__(self, name):
        try:
            return getattr(self._module, name)
        except AttributeError:
            raise AttributeError(f"{type(self)} object xxx has no attribute {name}")

    @staticmethod
    @deprecation.deprecated.favour("kvrlib.ean2ean_hi")
    def ean2ean_hi(ean):
        """Using KvrLib static functions is deprecated, all functionality has been
        moved to the kvrlib module itself."""
        return ean2ean_hi(ean)

    @staticmethod
    @deprecation.deprecated.favour("kvrlib.ean2ean_lo")
    def ean2ean_lo(ean):
        """Using KvrLib static functions is deprecated, all functionality has been
        moved to the kvrlib module itself."""
        return ean2ean_lo(ean)

    @staticmethod
    @deprecation.deprecated.favour("kvrlib.ean_hi_lo2ean")
    def ean_hi_lo2ean(ean_hi, ean_lo):
        """Using KvrLib static functions is deprecated, all functionality has been
        moved to the kvrlib module itself."""
        return ean_hi_lo2ean(ean_hi, ean_lo)
