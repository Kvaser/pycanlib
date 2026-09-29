import ctypes as ct

from .. import dllLoader
from .exceptions import lin_error
from .structures import MessageInfo

_no_errcheck = dllLoader.no_errcheck
c_LinHandle = ct.c_int


def _linReadTimer_errcheck(self, res, func, args):
    # in the event of a failure, `res` is the error code but type casted to an
    # unsigned long.
    raise NotImplementedError


class LINLibDll(dllLoader.MyDll):
    default_restype = ct.c_int

    # name: [[args], ret, errcheck]
    function_prototypes = {
        'linInitializeLibrary': [[], None, _no_errcheck],
        'linUnloadLibrary': [[], None, _no_errcheck],
        'linGetTransceiverData': [
            [ct.c_int, ct.POINTER(ct.c_char), ct.POINTER(ct.c_char), ct.POINTER(ct.c_int)]
        ],
        'linOpenChannel': [[ct.c_int, ct.c_int]],
        'linClose': [[c_LinHandle]],
        'linGetVersion': [[ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]],
        'linGetFirmwareVersion': [
            [
                c_LinHandle,
                ct.POINTER(ct.c_ubyte),
                ct.POINTER(ct.c_ubyte),
                ct.POINTER(ct.c_ubyte),
                ct.POINTER(ct.c_ubyte),
                ct.POINTER(ct.c_ubyte),
                ct.POINTER(ct.c_ubyte),
            ]
        ],
        'linGetChannelData': [[ct.c_int, ct.c_int, ct.c_void_p, ct.c_size_t]],
        'linSetBitrate': [[c_LinHandle, ct.c_uint]],
        'linBusOn': [[c_LinHandle]],
        'linBusOff': [[c_LinHandle]],
        # 'linReadTimer': [[c_LinHandle], ct.c_ulong, _linReadTimer_errcheck],
        'linWriteMessage': [[c_LinHandle, ct.c_uint, ct.c_void_p, ct.c_uint]],
        'linRequestMessage': [[c_LinHandle, ct.c_uint]],
        'linReadMessage': [
            [
                c_LinHandle,
                ct.POINTER(ct.c_uint),
                ct.c_void_p,
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                MessageInfo,
            ]
        ],
        'linReadMessageWait': [
            [
                c_LinHandle,
                ct.POINTER(ct.c_uint),
                ct.c_void_p,
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(MessageInfo),
                ct.c_ulong,
            ]
        ],
        'linUpdateMessage': [[c_LinHandle, ct.c_uint, ct.c_void_p, ct.c_uint]],
        'linSetupIllegalMessage': [[c_LinHandle, ct.c_uint, ct.c_uint, ct.c_uint]],
        'linSetupLIN': [[c_LinHandle, ct.c_uint, ct.c_uint]],
        'linWriteWakeup': [[c_LinHandle, ct.c_uint, ct.c_uint]],
        'linClearMessage': [[c_LinHandle, ct.c_uint]],
        'linWriteSync': [[c_LinHandle, ct.c_ulong]],
        'linGetCanHandle': [[c_LinHandle, ct.POINTER(ct.c_uint)]],
    }

    def __init__(self, ct_dll):
        super().__init__(ct_dll, **self.function_prototypes)

    def default_errcheck(self, result, func, arguments):
        """Error function used in ctype calls for LINlib DLL."""
        if result < 0:
            raise lin_error(result)
        else:
            return result
