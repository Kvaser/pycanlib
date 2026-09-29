import ctypes as ct
import sys

from .. import dllLoader
from .exceptions import can_error
from .structures import CanBusParamsTq, CanBusStatistics, kvTimeDomainData

_no_errcheck = dllLoader.no_errcheck

if sys.platform.startswith('win'):
    KVCALLBACK_T = ct.WINFUNCTYPE(None, ct.c_int, ct.c_void_p, ct.c_uint)
else:
    KVCALLBACK_T = ct.CFUNCTYPE(None, ct.c_int, ct.c_void_p, ct.c_uint)


class CanlibDll(dllLoader.MyDll):
    function_prototypes = {
        'canAccept': [[ct.c_int, ct.c_long, ct.c_uint]],
        'canBusOff': [[ct.c_int]],
        'canBusOn': [[ct.c_int]],
        'canClose': [[ct.c_int]],
        'canEnumHardwareEx': [[ct.POINTER(ct.c_int)]],
        'canGetBusOutputControl': [[ct.c_int, ct.POINTER(ct.c_uint)]],
        'canGetBusParams': [
            [
                ct.c_int,
                ct.POINTER(ct.c_long),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
            ]
        ],
        'canGetBusParamsFd': [
            [
                ct.c_int,
                ct.POINTER(ct.c_long),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
            ]
        ],
        'canGetBusParamsTq': [[ct.c_int, ct.POINTER(CanBusParamsTq)]],
        'canGetBusParamsFdTq': [
            [ct.c_int, ct.POINTER(CanBusParamsTq), ct.POINTER(CanBusParamsTq)]
        ],
        'canGetBusStatistics': [[ct.c_int, ct.POINTER(CanBusStatistics), ct.c_size_t]],
        'canGetChannelData': [[ct.c_int, ct.c_int, ct.c_void_p, ct.c_size_t]],
        'canGetErrorText': [[ct.c_int, ct.c_char_p, ct.c_uint]],
        'canGetHandleData': [[ct.c_int, ct.c_int, ct.c_void_p, ct.c_size_t]],
        'canGetNumberOfChannels': [[ct.POINTER(ct.c_int)]],
        'canRequestBusStatistics': [[ct.c_int]],
        'canGetVersion': [[], ct.c_short, _no_errcheck],  # Never fails (supposedly)
        'canGetVersionEx': [[ct.c_uint], ct.c_uint, _no_errcheck],  # Never fails
        'canInitializeLibrary': [[], None, _no_errcheck],  # Returns void, no errcheck function
        'canIoCtl': [[ct.c_int, ct.c_uint, ct.c_void_p, ct.c_uint]],
        'canObjBufAllocate': [[ct.c_int, ct.c_int]],
        'canObjBufDisable': [[ct.c_int, ct.c_int]],
        'canObjBufEnable': [[ct.c_int, ct.c_int]],
        'canObjBufFree': [[ct.c_int, ct.c_int]],
        'canObjBufFreeAll': [[ct.c_int]],
        'canObjBufSendBurst': [[ct.c_int, ct.c_int, ct.c_uint]],
        'canObjBufSetFilter': [[ct.c_int, ct.c_int, ct.c_uint, ct.c_uint]],
        'canObjBufSetFlags': [[ct.c_int, ct.c_int, ct.c_uint]],
        'canObjBufSetMsgCount': [[ct.c_int, ct.c_int, ct.c_uint]],
        'canObjBufSetPeriod': [[ct.c_int, ct.c_int, ct.c_uint]],
        'canObjBufWrite': [[ct.c_int, ct.c_int, ct.c_int, ct.c_void_p, ct.c_uint, ct.c_uint]],
        'canOpenChannel': [[ct.c_int, ct.c_int]],
        'canReadErrorCounters': [
            [ct.c_int, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]
        ],
        'canReadSpecificSkip': [
            [
                ct.c_int,
                ct.c_long,
                ct.c_void_p,
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_ulong),
            ]
        ],
        'canReadStatus': [[ct.c_int, ct.POINTER(ct.c_ulong)]],
        'canReadSyncSpecific': [[ct.c_int, ct.c_long, ct.c_ulong]],
        'canReadWait': [
            [
                ct.c_int,
                ct.POINTER(ct.c_long),
                ct.c_void_p,
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_ulong),
                ct.c_ulong,
            ]
        ],
        'canRequestChipStatus': [[ct.c_int]],
        'canSetAcceptanceFilter': [[ct.c_int, ct.c_uint, ct.c_uint, ct.c_int]],
        'canSetBusOutputControl': [[ct.c_int, ct.c_uint]],
        'canSetBusParams': [
            [ct.c_int, ct.c_long, ct.c_uint, ct.c_uint, ct.c_uint, ct.c_uint, ct.c_uint]
        ],
        'canSetBusParamsFd': [[ct.c_int, ct.c_long, ct.c_uint, ct.c_uint, ct.c_uint]],
        'canSetBusParamsTq': [[ct.c_int, CanBusParamsTq]],
        'canSetBusParamsFdTq': [[ct.c_int, CanBusParamsTq, CanBusParamsTq]],
        'canTranslateBaud': [
            [
                ct.POINTER(ct.c_long),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
            ]
        ],
        'canUnloadLibrary': [[]],
        'canWrite': [[ct.c_int, ct.c_long, ct.c_void_p, ct.c_uint, ct.c_uint]],
        'canWriteSync': [[ct.c_int, ct.c_long]],
        'canWriteWait': [[ct.c_int, ct.c_long, ct.c_void_p, ct.c_uint, ct.c_uint, ct.c_ulong]],
        'kvAnnounceIdentityEx': [[ct.c_int, ct.c_int, ct.c_void_p, ct.c_size_t]],
        'kvBitrateToBusParamsTq': [[ct.c_int, ct.c_int, ct.POINTER(CanBusParamsTq)]],
        'kvBitrateToBusParamsFdTq': [[ct.c_int, ct.c_int, ct.c_int, ct.POINTER(CanBusParamsTq), ct.POINTER(CanBusParamsTq)]],
        'kvDeviceGetMode': [[ct.c_int, ct.POINTER(ct.c_int)]],
        'kvDeviceSetMode': [[ct.c_int, ct.c_int]],
        'kvFileCopyFromDevice': [[ct.c_int, ct.c_char_p, ct.c_char_p]],
        'kvFileCopyToDevice': [[ct.c_int, ct.c_char_p, ct.c_char_p]],
        'kvFileDelete': [[ct.c_int, ct.c_char_p]],
        'kvFileDiskFormat': [[ct.c_int]],
        'kvFileGetCount': [[ct.c_int, ct.POINTER(ct.c_int)]],
        'kvFileGetName': [[ct.c_int, ct.c_int, ct.c_char_p, ct.c_int]],
        'kvFlashLeds': [[ct.c_int, ct.c_int, ct.c_int]],
        'kvIoConfirmConfig': [[ct.c_int]],
        'kvIoGetNumberOfPins': [[ct.c_int, ct.POINTER(ct.c_uint)]],
        'kvIoPinGetAnalog': [[ct.c_int, ct.c_uint, ct.POINTER(ct.c_float)]],
        'kvIoPinGetDigital': [[ct.c_int, ct.c_uint, ct.POINTER(ct.c_uint)]],
        'kvIoPinGetInfo': [[ct.c_int, ct.c_uint, ct.c_int, ct.c_void_p, ct.c_uint]],
        'kvIoPinGetOutputAnalog': [[ct.c_int, ct.c_uint, ct.POINTER(ct.c_float)]],
        'kvIoPinGetOutputDigital': [[ct.c_int, ct.c_uint, ct.POINTER(ct.c_uint)]],
        'kvIoPinGetOutputRelay': [[ct.c_int, ct.c_uint, ct.POINTER(ct.c_uint)]],
        'kvIoPinSetAnalog': [[ct.c_int, ct.c_uint, ct.c_float]],
        'kvIoPinSetDigital': [[ct.c_int, ct.c_uint, ct.c_uint]],
        'kvIoPinSetInfo': [[ct.c_int, ct.c_uint, ct.c_int, ct.c_void_p, ct.c_uint]],
        'kvIoPinSetRelay': [[ct.c_int, ct.c_uint, ct.c_uint]],
        'kvReadDeviceCustomerData': [[ct.c_int, ct.c_int, ct.c_int, ct.c_void_p, ct.c_size_t]],
        'kvReadTimer': [[ct.c_int, ct.POINTER(ct.c_int)]],
        'kvScriptEnvvarClose': [[ct.c_int64]],
        'kvScriptEnvvarGetData': [[ct.c_int64, ct.c_void_p, ct.c_int, ct.c_int]],
        'kvScriptEnvvarGetFloat': [[ct.c_int64, ct.POINTER(ct.c_float)]],
        'kvScriptEnvvarGetInt': [[ct.c_int64, ct.POINTER(ct.c_int)]],
        'kvScriptEnvvarOpen': [
            [ct.c_int, ct.c_char_p, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)],
            ct.c_int64,
        ],
        'kvScriptEnvvarSetData': [[ct.c_int64, ct.c_void_p, ct.c_int, ct.c_int]],
        'kvScriptEnvvarSetFloat': [[ct.c_int64, ct.c_float]],
        'kvScriptEnvvarSetInt': [[ct.c_int64, ct.c_int]],
        'kvScriptGetText': [
            [
                ct.c_int,
                ct.POINTER(ct.c_int),
                ct.POINTER(ct.c_ulong),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_char),
                ct.c_size_t,
            ]
        ],
        'kvScriptLoadFile': [[ct.c_int, ct.c_int, ct.c_char_p]],
        'kvScriptLoadFileOnDevice': [[ct.c_int, ct.c_int, ct.c_char_p]],
        'kvScriptRequestText': [[ct.c_int, ct.c_uint, ct.c_uint]],
        'kvScriptSendEvent': [[ct.c_int, ct.c_int, ct.c_int, ct.c_int, ct.c_uint]],
        'kvScriptStart': [[ct.c_int, ct.c_int]],
        'kvScriptStatus': [[ct.c_int, ct.c_int, ct.POINTER(ct.c_uint)]],
        'kvScriptStop': [[ct.c_int, ct.c_int, ct.c_int]],
        'kvScriptTxeGetData': [[ct.c_char_p, ct.c_int, ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvScriptUnload': [[ct.c_int, ct.c_int]],
        'kvSetNotifyCallback': [[ct.c_int, KVCALLBACK_T, ct.c_void_p, ct.c_uint]],
        'kvTimeDomainCreate': [[ct.POINTER(ct.c_void_p)]],
        'kvTimeDomainDelete': [[ct.c_void_p]],
        'kvTimeDomainAddHandle': [[ct.c_void_p, ct.c_int]],
        'kvTimeDomainRemoveHandle': [[ct.c_void_p, ct.c_int]],
        'kvTimeDomainGetData':[[ct.c_void_p, ct.POINTER(kvTimeDomainData), ct.c_size_t]],
        'kvTimeDomainResetTime':[[ct.c_void_p]],
    }

    def __init__(self, ct_dll):
        # set default values for function_prototypes
        self.default_restype = ct.c_int
        self.default_errcheck = self._error_check
        super().__init__(ct_dll, **self.function_prototypes)

    def _error_check(self, result, func, arguments):
        """Error function used in ctype calls for canlib DLL."""
        __tracebackhide__ = True
        if result < 0:
            raise can_error(result)
        else:
            return result
