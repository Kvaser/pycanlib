import ctypes as ct

from .. import dllLoader
from .enums import Error
from .events import memoLogEventEx
from .exceptions import kvm_error

_no_errcheck = dllLoader.no_errcheck
_kvmDeviceOpen_errcheck = dllLoader.errcheck_by_argp(status_pos=1, errortype=kvm_error)
_kvmKmfOpen_errcheck = dllLoader.errcheck_by_argp(status_pos=1, errortype=kvm_error)
_kvmKmfOpenEx_errcheck = dllLoader.errcheck_by_argp(status_pos=1, errortype=kvm_error)
_kvmKmfOpenEx_errcheck = dllLoader.errcheck_by_argp(status_pos=1, errortype=kvm_error)
_kvmKmeOpenFile_errcheck = dllLoader.errcheck_by_argp(status_pos=1, errortype=kvm_error)
_kvmKmeCreateFile_errcheck = dllLoader.errcheck_by_argp(status_pos=1, errortype=kvm_error)


def _kvmKmfReadConfig_errcheck(result, func, arguments):
    # If the buffer was too small, ILLEGAL_REQUEST is returned; but to handle
    # that case we need the return values (which contains the actual size of
    # the config).
    if result < 0 and result != Error.ILLEGAL_REQUEST:
        raise kvm_error(result)
    else:
        return result


class KvmlibDll(dllLoader.MyDll):
    function_prototypes = {
        'kvmClose': [[ct.c_void_p]],
        'kvmDeviceDiskSize': [[ct.c_void_p, ct.POINTER(ct.c_uint32)]],
        'kvmDeviceDiskStatus': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvmDeviceFlashLeds': [[ct.c_void_p]],
        'kvmDeviceFormatDisk': [[ct.c_void_p, ct.c_int, ct.c_uint32, ct.c_uint32]],
        'kvmDeviceGetRTC': [[ct.c_void_p, ct.POINTER(ct.c_uint32)]],
        'kvmDeviceGetSerialNumber': [[ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvmDeviceGetSoftwareInfo': [
            [
                ct.c_void_p,
                ct.c_int32,
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_uint),
            ]
        ],
        'kvmDeviceMountKmf': [[ct.c_int32]],
        'kvmDeviceMountKmfEx': [[ct.c_void_p, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]],
        'kvmDeviceOpen': [
            [ct.c_int32, ct.POINTER(ct.c_int), ct.c_int32],
            ct.c_void_p,
            _kvmDeviceOpen_errcheck,
        ],  # Returns handle
        'kvmDeviceSetRTC': [[ct.c_void_p, ct.c_uint32]],
        'kvmGetErrorText': [[ct.c_int32, ct.c_char_p, ct.c_size_t]],
        'kvmGetVersion': [[ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]],
        'kvmInitialize': [[], None, _no_errcheck],  # Returns void, no errcheck function
        'kvmKmeCloseFile': [[ct.c_void_p]],
        'kvmKmeCountEvents': [[ct.c_void_p, ct.POINTER(ct.c_uint32)]],
        'kvmKmeCountEventsEx': [[ct.c_void_p, ct.POINTER(ct.c_int64)]],
        'kvmKmeCreateFile': [
            [ct.c_char_p, ct.POINTER(ct.c_int32), ct.c_int32],
            ct.c_void_p,
            _kvmKmeCreateFile_errcheck,
        ],
        'kvmKmeOpenFile': [
            [ct.c_char_p, ct.POINTER(ct.c_int32), ct.c_int32],
            ct.c_void_p,
            _kvmKmeOpenFile_errcheck,
        ],
        'kvmKmeReadEvent': [[ct.c_void_p, ct.POINTER(memoLogEventEx)]],
        'kvmKmeScanFileType': [[ct.c_char_p, ct.POINTER(ct.c_int32)]],
        'kvmKmeWriteEvent': [[ct.c_void_p, ct.POINTER(memoLogEventEx)]],
        'kvmKmfGetUsage': [[ct.c_void_p, ct.POINTER(ct.c_uint32), ct.POINTER(ct.c_uint32)]],
        'kvmKmfOpen': [
            [ct.c_char_p, ct.POINTER(ct.c_int32), ct.c_int32],
            ct.c_void_p,
            _kvmKmfOpen_errcheck,
        ],
        'kvmKmfOpenEx': [
            [
                ct.c_char_p,
                ct.POINTER(ct.c_int32),
                ct.c_int32,
                ct.POINTER(ct.c_int),
                ct.POINTER(ct.c_int),
            ],
            ct.c_void_p,
            _kvmKmfOpenEx_errcheck,
        ],
        'kvmKmfReadConfig': [
            [ct.c_void_p, ct.c_void_p, ct.c_size_t, ct.POINTER(ct.c_size_t)],
            ct.c_int,
            _kvmKmfReadConfig_errcheck,
        ],
        'kvmKmfValidate': [[ct.c_void_p]],
        'kvmKmfWriteConfig': [[ct.c_void_p, ct.c_void_p, ct.c_uint]],
        'kvmLogFileDeleteAll': [[ct.c_void_p]],
        'kvmLogFileDismount': [[ct.c_void_p]],
        'kvmLogFileGetCount': [[ct.c_void_p, ct.POINTER(ct.c_uint32)]],
        'kvmLogFileGetType': [[ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_int32)]],
        'kvmLogFileGetCreatorSerial': [[ct.c_void_p, ct.POINTER(ct.c_uint32)]],
        'kvmLogFileGetEndTime': [[ct.c_void_p, ct.POINTER(ct.c_uint32)]],
        'kvmLogFileGetStartTime': [[ct.c_void_p, ct.POINTER(ct.c_uint32)]],
        'kvmLogFileMount': [[ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_uint32)]],
        'kvmLogFileMountEx': [[ct.c_void_p, ct.c_uint32, ct.POINTER(ct.c_int64)]],
        'kvmLogFileReadEvent': [[ct.c_void_p, ct.POINTER(memoLogEventEx)]],
    }

    def __init__(self, ct_dll):
        # set default values for function_prototypes
        self.default_restype = ct.c_int
        self.default_errcheck = self._error_check
        super().__init__(ct_dll, **self.function_prototypes)

    def _error_check(self, result, func, arguments):
        if result < 0:
            raise kvm_error(result)
        else:
            return result
