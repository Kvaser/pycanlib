import ctypes as ct

from .. import dllLoader
from .enums import Error
from .exceptions import kvr_error
from .structures import (kvrAddress, kvrCipherInfoElement, kvrDeviceInfo,
                         kvrVersion)

kvrConfigHandle = ct.c_int32
kvrRssiHistory = ct.c_int32
kvrRttHistory = ct.c_uint32

_no_errcheck = dllLoader.no_errcheck


def kvrConfigVerifyXml_errcheck(result, func, arguments):
    # CANlib v5.22 kvrERR_GENERIC means a problem was found
    # CANlib v5.23+ kvaERR_XML_VALIDATION means a problem was found
    if (
        result == 0
        or result == Error.XML_VALIDATION
        or result == Error.GENERIC
        or result == Error.BUFFER_TOO_SMALL
    ):
        return result
    else:
        raise kvr_error(result)


class KvrlibDll(dllLoader.MyDll):
    function_prototypes = {
        'kvrGetVersion': [[], kvrVersion, _no_errcheck],  # No error function
        'kvrAddressFromString': [[ct.c_int32, ct.POINTER(kvrAddress), ct.c_char_p]],
        'kvrStringFromAddress': [[ct.c_char_p, ct.c_uint32, ct.POINTER(kvrAddress)]],
        'kvrDeviceGetServiceStatus': [
            [ct.POINTER(kvrDeviceInfo), ct.POINTER(ct.c_int32), ct.POINTER(ct.c_int32)]
        ],
        'kvrDeviceGetServiceStatusText': [[ct.POINTER(kvrDeviceInfo), ct.c_char_p, ct.c_uint32]],
        'kvrDiscoveryClearDevicesAtExit': [[ct.c_uint]],
        'kvrDiscoveryClose': [[ct.c_int32]],
        'kvrDiscoveryOpen': [[ct.POINTER(ct.c_int32)]],
        'kvrDiscoveryGetDefaultAddresses': [
            [ct.POINTER(kvrAddress), ct.c_uint32, ct.POINTER(ct.c_uint32), ct.c_uint32]
        ],
        'kvrDiscoveryGetResults': [[ct.c_int32, ct.POINTER(kvrDeviceInfo)]],
        'kvrDiscoverySetAddresses': [[ct.c_int32, ct.POINTER(kvrAddress), ct.c_uint32]],
        'kvrDiscoverySetEncryptionKey': [[ct.POINTER(kvrDeviceInfo), ct.c_char_p]],
        'kvrDiscoverySetPassword': [[ct.POINTER(kvrDeviceInfo), ct.c_char_p]],
        'kvrDiscoveryStart': [[ct.c_int32, ct.c_uint32, ct.c_uint32]],
        'kvrDiscoveryStartEx': [[ct.c_int32, ct.c_uint32, ct.c_uint32, ct.c_int]],
        'kvrDiscoveryStoreDevices': [[ct.POINTER(kvrDeviceInfo), ct.c_uint32]],
        'kvrConfigActiveProfileSet': [[ct.c_int32, ct.c_int32]],
        'kvrConfigActiveProfileGet': [[ct.c_int32, ct.POINTER(ct.c_int32)]],
        'kvrConfigNoProfilesGet': [[ct.c_int32, ct.POINTER(ct.c_int32)]],
        'kvrConfigClose': [[ct.c_int32], None, _no_errcheck],  # Returns void, never fails
        'kvrConfigOpen': [[ct.c_int32, ct.c_int32, ct.POINTER(ct.c_char), ct.POINTER(ct.c_int32)]],
        'kvrConfigClear': [[ct.c_int32]],
        'kvrConfigOpenEx': [
            [ct.c_int32, ct.c_int32, ct.POINTER(ct.c_char), ct.POINTER(ct.c_int32), ct.c_uint32]
        ],
        'kvrConfigSet': [[ct.c_int32, ct.c_char_p]],
        'kvrConfigGet': [[ct.c_int32, ct.c_char_p, ct.c_uint32]],
        'kvrConfigInfoGet': [[ct.c_int32, ct.c_int32, ct.c_char_p, ct.c_uint32]],
        'kvrConfigVerifyXml': [
            [ct.c_char_p, ct.c_char_p, ct.c_uint32],
            ct.c_int32,
            kvrConfigVerifyXml_errcheck,
        ],
        'kvrGetErrorText': [[ct.c_int32, ct.c_char_p, ct.c_uint32]],
        'kvrInitializeLibrary': [[], None, _no_errcheck],  # Returns void, no errcheck function
        'kvrHostName': [[ct.c_uint32, ct.c_uint32, ct.c_uint32, ct.c_char_p, ct.c_uint32]],
        'kvrNetworkConnectionTest': [[ct.c_int32, ct.c_int32]],
        'kvrNetworkGetHostName': [[kvrConfigHandle, ct.POINTER(ct.c_char), ct.c_uint32]],
        'kvrNetworkGetConnectionStatus': [
            [
                kvrConfigHandle,
                ct.POINTER(ct.c_int32),
                ct.POINTER(ct.c_int32),
                ct.POINTER(ct.c_int32),
                ct.POINTER(ct.c_int32),
                ct.POINTER(ct.c_int32),
                ct.POINTER(ct.c_int32),
            ]
        ],
        'kvrNetworkGenerateWepKeys': [
            [ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p]
        ],
        'kvrNetworkGenerateWpaKeys': [[ct.c_char_p, ct.c_char_p, ct.c_char_p]],
        'kvrNetworkGetRssiRtt': [
            [
                kvrConfigHandle,
                ct.POINTER(kvrRssiHistory),
                ct.c_uint32,
                ct.POINTER(ct.c_uint32),
                ct.POINTER(kvrRttHistory),
                ct.c_uint32,
                ct.POINTER(ct.c_uint32),
            ]
        ],
        'kvrNetworkGetAddressInfo': [
            [
                kvrConfigHandle,
                ct.POINTER(kvrAddress),
                ct.POINTER(kvrAddress),
                ct.POINTER(kvrAddress),
                ct.POINTER(kvrAddress),
                ct.POINTER(ct.c_int32),
            ]
        ],
        'kvrUnloadLibrary': [[], None, _no_errcheck],
        'kvrServiceQuery': [[ct.POINTER(ct.c_int)]],
        'kvrServiceStart': [[ct.POINTER(ct.c_int)]],
        'kvrServiceStop': [[ct.POINTER(ct.c_int)]],
        'kvrWlanStartScan': [[kvrConfigHandle, ct.c_int32, ct.c_int32, ct.c_int32]],
        'kvrWlanGetScanResults': [
            [
                kvrConfigHandle,
                ct.POINTER(ct.c_int32),
                ct.POINTER(ct.c_int32),
                ct.POINTER(kvrAddress),
                ct.POINTER(ct.c_int32),
                ct.POINTER(ct.c_char),
                ct.POINTER(ct.c_uint32),
                ct.POINTER(ct.c_uint32),
                ct.POINTER(kvrCipherInfoElement),
                ct.POINTER(kvrCipherInfoElement),
            ]
        ],
        'kvrWlanGetSecurityText': [
            [
                ct.c_char_p,
                ct.c_uint32,
                ct.c_uint32,
                ct.c_uint32,
                kvrCipherInfoElement,
                kvrCipherInfoElement,
            ]
        ],
    }

    def __init__(self, ct_dll):
        # set default values for function_prototypes
        self.default_restype = ct.c_int
        self.default_errcheck = self._error_check
        super().__init__(ct_dll, **self.function_prototypes)

    def _error_check(self, result, func, arguments):
        if result < 0:
            raise kvr_error(result)
        else:
            return result
