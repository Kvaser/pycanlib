import ctypes as ct

from canlib import dllLoader

from .enums import (ProtocolProperties, ProtocolType, SignalByteOrder,
                    SignalType)
from .exceptions import kvd_error


class KvaDbDll(dllLoader.MyDll):
    function_prototypes = {
        'kvaDbAddAttribute': [[ct.c_void_p, ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbAddAttributeDefinition': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbAddAttributeDefinitionEnum': [[ct.c_void_p, ct.c_char_p, ct.c_int]],
        'kvaDbAddEnumValue': [[ct.c_void_p, ct.c_int, ct.c_char_p]],
        'kvaDbAddMsg': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbAddMsgAttribute': [[ct.c_void_p, ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbAddNodeAttribute': [[ct.c_void_p, ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbAddReceiveNodeToSignal': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbRemoveReceiveNodeFromSignal': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbAddSignal': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbAddSignalAttribute': [[ct.c_void_p, ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbAddNode': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbBytesToMsgDlc': [[ProtocolType, ct.c_uint, ct.POINTER(ct.c_uint)]],
        'kvaDbClose': [[ct.c_void_p]],
        'kvaDbCreate': [[ct.c_void_p, ct.c_char_p, ct.c_char_p]],
        'kvaDbDeleteAttribute': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbDeleteAttributeDefinition': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbDeleteEnumValue': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbDeleteMsg': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbDeleteMsgAttribute': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbDeleteNode': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbDeleteNodeAttribute': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbDeleteSignalAttribute': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbDeleteSignal': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbOpen': [[ct.POINTER(ct.c_void_p)]],
        'kvaDbGetAttributeByName': [[ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetAttributeDefinitionByName': [[ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetAttributeDefinitionEnumeration': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetAttributeDefinitionEnumFirst': [
            [ct.c_void_p, ct.POINTER(ct.c_int), ct.c_char_p, ct.POINTER(ct.c_size_t)]
        ],
        'kvaDbGetAttributeDefinitionEnumNext': [
            [ct.c_void_p, ct.POINTER(ct.c_int), ct.c_char_p, ct.POINTER(ct.c_size_t)]
        ],
        'kvaDbGetAttributeDefinitionFloat': [
            [ct.c_void_p, ct.POINTER(ct.c_float), ct.POINTER(ct.c_float), ct.POINTER(ct.c_float)]
        ],
        'kvaDbGetAttributeDefinitionInt': [
            [ct.c_void_p, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]
        ],
        'kvaDbGetAttributeDefinitionOwner': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetAttributeDefinitionName': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetAttributeDefinitionType': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetAttributeDefinitionString': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetAttributeName': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetAttributeType': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetAttributeValueEnumeration': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetAttributeValueFloat': [[ct.c_void_p, ct.POINTER(ct.c_float)]],
        'kvaDbGetAttributeValueInt': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetAttributeValueString': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetCanMsgFlags': [[ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvaDbGetDatabaseName': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetEnumValue': [[ct.c_void_p, ct.POINTER(ct.c_int), ct.c_char_p, ct.c_size_t]],
        'kvaDbGetErrorText': [[ct.c_int32, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetFirstAttributeDefinition': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetFirstEnumValue': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetFirstMsg': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetFirstMsgAttribute': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetFirstNode': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetFirstNodeAttribute': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetFirstSignal': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetFirstSignalAttribute': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetFlags': [[ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvaDbGetFirstAttribute': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetLastParseError': [[ct.c_char_p, ct.POINTER(ct.c_uint)]],
        'kvaDbGetNextAttribute': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetNextAttributeDefinition': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetNextEnumValue': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetNextMsg': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetNextNode': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetNextSignal': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetMsgAttributeByName': [[ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetMsgById': [[ct.c_void_p, ct.c_uint, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetMsgByIdEx': [[ct.c_void_p, ct.c_uint, ct.c_uint, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetMsgByName': [[ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetMsgByPGN': [[ct.c_void_p, ct.c_int, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetMsgByPGNEx': [[ct.c_void_p, ct.c_int, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetMsgComment': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetMsgDlc': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetMsgId': [[ct.c_void_p, ct.POINTER(ct.c_uint), ct.POINTER(ct.c_uint)]],
        'kvaDbGetMsgIdEx': [[ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvaDbGetMsgFlags': [[ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvaDbGetMsgName': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetMsgQualifiedName': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetMsgSendNode': [[ct.c_void_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetNodeAttributeByName': [[ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetNodeByName': [[ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetNodeName': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetNodeComment': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetProtocol': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetProtocolProperties': [[ProtocolType, ct.POINTER(ProtocolProperties)]],
        'kvaDbGetSignalAttributeByName': [[ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetSignalByName': [[ct.c_void_p, ct.c_char_p, ct.POINTER(ct.c_void_p)]],
        'kvaDbGetSignalComment': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetSignalEncoding': [[ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvaDbGetSignalMode': [[ct.c_void_p, ct.POINTER(ct.c_int)]],
        'kvaDbGetSignalName': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetSignalQualifiedName': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetSignalRepresentationType': [[ct.c_void_p, ct.POINTER(ct.c_uint)]],
        'kvaDbGetSignalUnit': [[ct.c_void_p, ct.c_char_p, ct.c_size_t]],
        'kvaDbGetSignalValueLimits': [
            [ct.c_void_p, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
        ],
        'kvaDbGetSignalValueScaling': [
            [ct.c_void_p, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
        ],
        'kvaDbGetSignalValueSize': [[ct.c_void_p, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]],
        'kvaDbGetVersion': [[ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int)]],
        'kvaDbMsgDlcToBytes': [[ProtocolType, ct.c_uint, ct.POINTER(ct.c_uint)]],
        'kvaDbRetrieveSignalValuePhys': [
            [ct.c_void_p, ct.POINTER(ct.c_double), ct.c_void_p, ct.c_size_t]
        ],
        'kvaDbRetrieveSignalValueRaw64': [
            [ct.c_void_p, ct.POINTER(ct.c_uint64), ct.c_void_p, ct.c_size_t]
        ],
        'kvaDbSetAttributeDefinitionEnumDefault': [[ct.c_void_p, ct.c_int]],
        'kvaDbSetAttributeDefinitionFloat': [[ct.c_void_p, ct.c_float, ct.c_float, ct.c_float]],
        'kvaDbSetAttributeDefinitionInt': [[ct.c_void_p, ct.c_int, ct.c_int, ct.c_int]],
        'kvaDbSetAttributeDefinitionName': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetAttributeDefinitionOwner': [[ct.c_void_p, ct.c_uint]],
        'kvaDbSetAttributeDefinitionString': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetAttributeDefinitionType': [[ct.c_void_p, ct.c_int]],
        'kvaDbSetAttributeValueEnumeration': [[ct.c_void_p, ct.c_int]],
        'kvaDbSetAttributeValueFloat': [[ct.c_void_p, ct.c_float]],
        'kvaDbSetAttributeValueInt': [[ct.c_void_p, ct.c_int]],
        'kvaDbSetAttributeValueString': [[ct.c_void_p, ct.c_char_p, ct.c_int]],
        'kvaDbSetFlags': [[ct.c_void_p, ct.c_uint]],
        'kvaDbSetMsgComment': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetMsgDlc': [[ct.c_void_p, ct.c_int]],
        'kvaDbSetMsgId': [[ct.c_void_p, ct.c_uint, ct.c_uint]],
        'kvaDbSetMsgIdEx': [[ct.c_void_p, ct.c_uint]],
        'kvaDbSetMsgFlags': [[ct.c_void_p, ct.c_uint]],
        'kvaDbSetMsgName': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetMsgSendNode': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbSetNodeComment': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetNodeName': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetProtocol': [[ct.c_void_p, ProtocolType]],
        'kvaDbSetSignalComment': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetSignalEncoding': [[ct.c_void_p, SignalByteOrder]],
        'kvaDbSetSignalMode': [[ct.c_void_p, ct.c_int]],
        'kvaDbSetSignalName': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetSignalRepresentationType': [[ct.c_void_p, SignalType]],
        'kvaDbSetSignalUnit': [[ct.c_void_p, ct.c_char_p]],
        'kvaDbSetSignalValueLimits': [[ct.c_void_p, ct.c_double, ct.c_double]],
        'kvaDbSetSignalValueScaling': [[ct.c_void_p, ct.c_double, ct.c_double]],
        'kvaDbSetSignalValueSize': [[ct.c_void_p, ct.c_int, ct.c_int]],
        'kvaDbSignalContainsReceiveNode': [[ct.c_void_p, ct.c_void_p]],
        'kvaDbStoreSignalValuePhys': [[ct.c_void_p, ct.c_void_p, ct.c_int, ct.c_double]],
        'kvaDbStoreSignalValueRaw64': [[ct.c_void_p, ct.c_void_p, ct.c_int, ct.c_uint64]],
        'kvaDbWriteFile': [[ct.c_void_p, ct.c_char_p]],
    }

    def __init__(self, ct_dll):
        # set default values for function_prototypes
        self.default_restype = ct.c_int
        self.default_errcheck = self._error_check
        super().__init__(ct_dll, **self.function_prototypes)

    def _error_check(self, result, func, arguments):
        __tracebackhide__ = True
        if result < 0:
            raise kvd_error(result)
        else:
            return result
