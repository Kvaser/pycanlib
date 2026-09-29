import ctypes as ct

from .. import dllLoader
from .exceptions import kvlc_error


class KvlclibDll(dllLoader.MyDll):
    function_prototypes = {
        'kvlcAddDatabaseFile': [[ct.c_void_p, ct.c_char_p, ct.c_uint]],
        'kvlcAttachFile': [[ct.c_void_p, ct.c_char_p]],
        'kvlcConvertEvent': [[ct.c_void_p]],
        'kvlcCreateConverter': [[ct.c_void_p, ct.c_char_p, ct.c_int]],
        'kvlcDeleteConverter': [[ct.c_void_p]],
        'kvlcEventCount': [[ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvlcEventCountEx': [[ct.c_void_p, ct.POINTER(ct.c_int64)]],
        'kvlcFeedSelectFormat': [[ct.c_void_p, ct.c_int]],
        'kvlcFeedLogEvent': [[ct.c_void_p, ct.c_void_p]],
        'kvlcFeedNextFile': [[ct.c_void_p]],
        'kvlcGetDlcMismatchList': [[ct.c_void_p, ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint)]],
        'kvlcGetErrorText': [[ct.c_int32, ct.c_char_p, ct.c_uint]],
        'kvlcGetFirstWriterFormat': [[ct.POINTER(ct.c_int)]],
        'kvlcGetNextWriterFormat': [[ct.c_int, ct.POINTER(ct.c_int)]],
        'kvlcGetOutputFilename': [[ct.c_void_p, ct.c_char_p, ct.c_int]],
        'kvlcGetProperty': [[ct.c_void_p, ct.c_uint, ct.c_void_p, ct.c_size_t]],
        'kvlcGetVersion': [[ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]],
        'kvlcGetWriterDescription': [[ct.c_int, ct.c_char_p, ct.c_int]],
        'kvlcGetWriterExtension': [[ct.c_int, ct.c_char_p, ct.c_int]],
        'kvlcGetWriterName': [[ct.c_int, ct.c_char_p, ct.c_int]],
        'kvlcGetWriterPropertyDefault': [[ct.c_int, ct.c_uint, ct.c_void_p, ct.c_size_t]],
        'kvlcGetFirstReaderFormat': [[ct.POINTER(ct.c_int)]],
        'kvlcGetNextReaderFormat': [[ct.c_int, ct.POINTER(ct.c_int)]],
        'kvlcGetReaderDescription': [[ct.c_int, ct.c_char_p, ct.c_int]],
        'kvlcGetReaderExtension': [[ct.c_int, ct.c_char_p, ct.c_int]],
        'kvlcGetReaderName': [[ct.c_int, ct.c_char_p, ct.c_int]],
        'kvlcGetReaderPropertyDefault': [[ct.c_int, ct.c_uint, ct.c_void_p, ct.c_size_t]],
        'kvlcIsDataTruncated': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvlcIsDlcMismatch': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvlcIsOutputFilenameNew': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvlcIsOverrunActive': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvlcIsPropertySupported': [[ct.c_int, ct.c_uint, ct.POINTER(ct.c_int)]],
        'kvlcNextInputFile': [[ct.c_void_p, ct.c_char_p]],
        'kvlcResetDataTruncated': [[ct.c_void_p]],
        'kvlcResetDlcMismatch': [[ct.c_void_p]],
        'kvlcResetOverrunActive': [[ct.c_void_p]],
        'kvlcSetInputFile': [[ct.c_void_p, ct.c_char_p, ct.c_int]],
        'kvlcSetProperty': [[ct.c_void_p, ct.c_uint, ct.c_void_p, ct.c_size_t]],
    }

    def __init__(self, ct_dll):
        # set default values for function_prototypes
        self.default_restype = ct.c_int
        self.default_errcheck = self._error_check
        super().__init__(ct_dll, **self.function_prototypes)

    def _error_check(self, result, func, arguments):
        __tracebackhide__ = True
        if result < 0:
            raise kvlc_error(result)
        else:
            return result
