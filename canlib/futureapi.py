"""futureapi -- module for handling functions not necessarily present

This module defines a number of function with the same name as a C function
newly added to one of the CANlib dlls. When `dllLoader.MyDll` can't find a
foreign function specified in a ``function_prototypes``, it consults this
module; if a function with an identical name exists in this module that
function will be used instead.

This allows us to essentially monkey-patch our C dlls.

Each function needs to have an identical name to the C function it is supposed
to patch and should for clarity's sake have the same arguments. It should also
immediately raise `NotYetSupportedError` (defined in this module) with a
message saying what is not yet supported and when (what version) it will be
supported.

"""
from .exceptions import CanlibException


class NotYetSupportedError(CanlibException, NotImplementedError):
    """An operation that is not yet supported by the loaded dll was attempted"""

    pass


def linGetVersion(major, minor, build):
    raise NotYetSupportedError("Accessing LINlib version requires CANlib SDK v5.23 or newer.")


def kvaDbGetAttributeByName(dh, attrName, ah):
    raise NotYetSupportedError(
        "Reading database attributes (by name) requires CANlib SDK v5.23 or newer."
    )


def kvaDbGetFirstAttribute(dh, nah):
    raise NotYetSupportedError("Reading database attributes requires CANlib SDK v5.23 or newer.")


def kvaDbAddAttribute(dh, adh, ah):
    raise NotYetSupportedError("Adding database attribute requires CANlib SDK v5.23 or newer.")


def kvaDbDeleteAttribute(dh, ah):
    raise NotYetSupportedError("Deleting database attribute requires CANlib SDK v5.23 or newer.")


def kvScriptTxeGetData(*args):
    raise NotYetSupportedError(
        "Accessing CANlib kvScriptTxeGetData requires Windows CANlib SDK v5.23, Linux CANlib SDK v5.25 or newer."
    )


def kvScriptGetText(hnd, slot, time, flags, buf, bufsize):
    raise NotYetSupportedError(
        "Getting text from script (kvScriptRequestText and kvScriptGetText) is only supported on Windows."
    )


def kvScriptRequestText(hnd, slot, request):
    raise NotYetSupportedError(
        "Getting text from script (kvScriptRequestText and kvScriptGetText) is only supported on Windows."
    )


def canGetVersionEx(itemCode):
    raise NotYetSupportedError(
        "Accessing canGetVersionEx in Linux requires CANlib SDK v5.23 or newer."
    )


def kvaDbGetAttributeDefinitionEnumFirst(adh, eValue, eName, buflen):
    raise NotYetSupportedError(
        "Accessing kvadblib kvaDbGetAttributeDefinitionEnumFirst requires CANlib SDK v5.23 or newer."
    )


def kvaDbGetAttributeDefinitionEnumNext(adh, eValue, eName, buflen):
    raise NotYetSupportedError(
        "Accessing kvadblib kvaDbGetAttributeDefinitionEnumNext requires CANlib SDK v5.23 or newer."
    )


def kvlcGetFirstReaderFormat(format):
    raise NotYetSupportedError("Accessing Reader Formats requires CANlib SDK v5.25 or newer.")


def kvlcGetNextReaderFormat(currentFormat, nextFormat):
    raise NotYetSupportedError("Accessing Reader Formats requires CANlib SDK v5.25 or newer.")


def kvlcGetReaderDescription(format, str, len):
    raise NotYetSupportedError("Accessing Reader Formats requires CANlib SDK v5.25 or newer.")


def kvlcGetReaderExtension(format, str, len):
    raise NotYetSupportedError("Accessing Reader Formats requires CANlib SDK v5.25 or newer.")


def kvlcGetReaderName(format, str, len):
    raise NotYetSupportedError("Accessing Reader Formats requires CANlib SDK v5.25 or newer.")


def kvlcGetReaderPropertyDefault(format, property, buf, len):
    raise NotYetSupportedError("Accessing Reader Formats requires CANlib SDK v5.25 or newer.")


def kvaDbDeleteAttributeDefinition(db, adh):
    raise NotYetSupportedError("Accessing Reader Formats requires CANlib SDK v5.25 or newer.")


def kvIoConfirmConfig(hnd):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoGetNumberOfPins(hnd, pinCount):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinGetInfo(hnd, pin, item, buffer, bufsize):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinGetAnalog(hnd, pin, value):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinGetOutputAnalog(hnd, pin, value):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinGetDigital(hnd, pin, value):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinGetOutputDigital(hnd, pin, value):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinSetAnalog(hnd, pin, value):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinSetDigital(hnd, pin, value):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinSetRelay(hnd, pin, value):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinGetOutputRelay(hnd, pin, value):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvIoPinSetInfo(hnd, pin, item, buffer, bufsize):
    raise NotYetSupportedError("Accessing I/O Pin Handling requires CANlib SDK v5.26 or newer.")


def kvlcGetDlcMismatchList(hnd, MsgIds, MsgDlc, MsgOccurance, length):
    raise NotYetSupportedError(
        "Accessing Dlc Mismatch Handling requires CANlib SDK v5.27 or newer."
    )


def kvlcIsDlcMismatch(hnd, mismatch):
    raise NotYetSupportedError(
        "Accessing Dlc Mismatch Handling requires CANlib SDK v5.27 or newer."
    )


def kvlcResetDlcMismatch(hnd):
    raise NotYetSupportedError(
        "Accessing Dlc Mismatch Handling requires CANlib SDK v5.27 or newer."
    )


def kvaDbGetLastParseError(buf, buflen):
    raise NotYetSupportedError(
        "Accessing kvaDbGetLastParseError requires CANlib SDK v5.28 or newer."
    )


def kvmLogFileMountEx(hnd, fileIndx, eventCount):
    raise NotYetSupportedError("Accessing kvmLogFileMountEx requires CANlib SDK v5.29 or newer.")


def kvlcEventCountEx(hnd, count):
    raise NotYetSupportedError("Accessing kvlcEventCountEx requires CANlib SDK v5.29 or newer.")


def kvmKmeCountEventsEx(hnd, eventCount):
    raise NotYetSupportedError("Accessing kvmKmeCountEventsEx requires CANlib SDK v5.29 or newer.")


def kvFileDiskFormat(hnd):
    raise NotYetSupportedError("Accessing kvFileDiskFormat requires CANlib SDK v5.29 or newer.")


def kvmLogFileGetType(hnd, fileIndx, logFileType):
    raise NotYetSupportedError("Accessing kvmLogFileGetType requires CANlib SDK v5.29 or newer.")


def canEnumHardwareEx(channelCount):
    raise NotYetSupportedError("Accessing canEnumHardwareEx requires CANlib SDK v5.31 or newer.")


def canSetBusParamsTq(hnd, nominal):
    raise NotYetSupportedError("Accessing canSetBusParamsTq requires CANlib SDK v5.34 or newer.")


def canGetBusParamsTq(hnd, nominal):
    raise NotYetSupportedError("Accessing canGetBusParamsTq requires CANlib SDK v5.34 or newer.")


def canSetBusParamsFdTq(hnd, nominal, data):
    raise NotYetSupportedError("Accessing canSetBusParamsFdTq requires CANlib SDK v5.34 or newer.")


def canGetBusParamsFdTq(hnd, nominal, data):
    raise NotYetSupportedError("Accessing canGetBusParamsFdTq requires CANlib SDK v5.34 or newer.")


def kvaDbGetMsgByIdEx(dh, nah):
    raise NotYetSupportedError("Reading database attributes requires CANlib SDK v5.34 or newer.")


def kvaDbGetMsgByPGNEx(dh, nah):
    raise NotYetSupportedError("Accessing kvaDbGetMsgByPGNEx requires CANlib SDK v5.34 or newer.")


def kvBitrateToBusParamsTq(hnd, freq, nominal):
    raise NotYetSupportedError(
        "Translating can_BITRATE_xxx constants to corresponding bus parameter values requires CANlib SDK v5.35 or newer."
    )


def kvBitrateToBusParamsFdTq(hnd, freqA, freqD, arbitration, data):
    raise NotYetSupportedError(
        "Translating canFD_BITRATE_xxx constants to corresponding bus parameter values requires CANlib SDK v5.35 or newer."
    )


def kvaDbGetCanMsgFlags(hnd, flags):
    raise NotYetSupportedError(
        "Reading CAN message flags from kvadblib requires CANlib SDK v5.39 or newer."
    )
