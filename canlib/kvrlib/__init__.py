"""Wrapper for the Kvaser kvrlib library

Some Kvaser devices, known as remote devices, can be connected via Ethernet
(E.g. Kvaser Ethercan Light HS and Kvaser BlackBird v2) and you need to
configure those devices before they are connected to your computer. This is
where kvrlib comes into play with functions to discover and connect to a Kvaser
Device on the network, making it accessible for the CANlib functions. The
kvrlib also has functions to configure how the remote device connects to the
network (e.g. dynamic/static IP). It also contains extra functions for wireless
setup, such as scanning and getting connection status.

"""

from . import service
from .constants import *
from .discovery import (Address, DeviceInfo, Discovery, ServiceStatus,
                        get_default_discovery_addresses, openDiscovery,
                        set_clear_stored_devices_on_exit, start_discovery,
                        store_devices, stored_devices)
from .enums import (Accessibility, AddressType, AddressTypeFlag, Availability,
                    BasicServiceSet, ConfigMode, DeviceUsage, Error,
                    NetworkState, RegulatoryDomain, RemoteState, ServiceState,
                    StartInfo)
from .exceptions import KvrBlank, KvrError
from .infoset import (DeviceInfoSet, DeviceNotInSetError, discover_info_set,
                      empty_info_set, stored_info_set)
from .remotedevice import (AddressInfo, ConfigProfile, ConnectionStatus,
                           ConnectionTest, ConnectionTestResult, RemoteDevice,
                           WlanScan, WlanScanResult, openDevice)
from .structures import (kvrAddress, kvrAddressList, kvrDeviceInfo,
                         kvrDeviceInfoList, kvrVersion)
from .wrapper import KvrLib
from .wrapper import KvrLib as kvrlib
from .wrapper import (WEPKeys, addressFromString, configActiveProfileGet,
                      configActiveProfileSet, configNoProfilesGet,
                      deviceGetServiceStatus, deviceGetServiceStatusText,
                      dllversion, ean2ean_hi, ean2ean_lo, ean_hi_lo2ean,
                      generate_wep_keys, generate_wpa_keys, getVersion,
                      hostname, initializeLibrary, kvrConfig, kvrDiscovery,
                      stringFromAddress, unload, verify_xml)

# for backwards compatibility
kvrDeviceUsage = DeviceUsage
kvrAccessibility = Accessibility
kvrAvailability = Availability
kvrError = KvrError
kvrBlank = KvrBlank
