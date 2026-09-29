import ctypes as ct

from .. import dllLoader
from .exceptions import kva_error


class KvaMemoLibXmlDll(dllLoader.MyDll):
    function_prototypes = {
        'kvaXmlInitialize': [[]],
        'kvaXmlGetVersion': [[], ct.c_short, dllLoader.no_errcheck],
        'kvaXmlValidate': [[ct.c_char_p, ct.c_uint]],
        'kvaXmlGetValidationStatusCount': [[ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]],
        'kvaXmlGetValidationError': [[ct.POINTER(ct.c_int), ct.c_char_p, ct.c_uint]],
        'kvaXmlGetValidationWarning': [[ct.POINTER(ct.c_int), ct.c_char_p, ct.c_uint]],
        'kvaXmlGetErrorText': [[ct.c_int, ct.c_char_p, ct.c_int]],
        'kvaXmlGetLastError': [[ct.c_char_p, ct.c_uint, ct.POINTER(ct.c_int)]],
        'kvaBufferToXml': [
            [
                ct.c_char_p,
                ct.c_uint,
                ct.c_char_p,
                ct.POINTER(ct.c_uint),
                ct.POINTER(ct.c_long),
                ct.c_char_p,
            ]
        ],
        'kvaXmlToBuffer': [
            [ct.c_char_p, ct.c_uint, ct.c_char_p, ct.POINTER(ct.c_uint), ct.POINTER(ct.c_long)]
        ],
        'kvaXmlToFile': [[ct.c_char_p, ct.c_char_p]],
    }

    def __init__(self, ct_dll):
        # set default values for function_prototypes
        self.default_restype = ct.c_int
        self.default_errcheck = self._error_check
        super().__init__(ct_dll, **self.function_prototypes)

    def _error_check(self, result, func, arguments):
        if result < 0:
            raise kva_error(result)
        return result
