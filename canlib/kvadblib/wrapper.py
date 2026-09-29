"""Wrapper for Kvaser Database API (kvaDbLib)."""

import ctypes as ct

from canlib import dllLoader

from .dll import KvaDbDll
from .enums import ProtocolProperties
from .exceptions import KvdBufferTooSmall


# qqqmac replace with global VersionNumber class
class kvadbVersion:
    """
    Class that holds kvadblib version number.

    """

    def __init__(self, major, minor, build):
        self.major = major
        self.minor = minor
        self.build = build

    def __str__(self):
        """
        Presents the version number as 'major.minor.build'.
        """
        return f"{self.major}.{self.minor}.{self.build}"


def bytes_to_dlc(num_bytes, protocol):
    """Convert number of bytes to DLC for given protocol."""
    dlc = ct.c_uint()
    dll.kvaDbBytesToMsgDlc(protocol, num_bytes, ct.byref(dlc))
    return dlc.value


def dlc_to_bytes(dlc, protocol):
    """Convert DLC to number of bytes for given protocol."""
    num_bytes = ct.c_uint()
    dll.kvaDbMsgDlcToBytes(protocol, dlc, ct.byref(num_bytes))
    return num_bytes.value


def get_protocol_properties(prot):
    """Get the signal protocol_properties."""
    p = ProtocolProperties()
    dll.kvaDbGetProtocolProperties(prot, ct.byref(p))
    return p


def dllversion():
    """Get the kvaDbLib DLL version number as a `VersionNumber`"""
    c_major = ct.c_int()
    c_minor = ct.c_int()
    c_build = ct.c_int()
    dll.kvaDbGetVersion(ct.byref(c_major), ct.byref(c_minor), ct.byref(c_build))
    return kvadbVersion(major=c_major.value, minor=c_minor.value, build=c_build.value)


def get_last_parse_error():
    """
    Can be used to get the specific reason why `KvdDbFileParse` was raised.

    Returns:
        `str`: Error message from the parser.

    .. versionadded:: 1.10

    """
    buflen_pre = 512
    buflen = ct.pointer(ct.c_uint(buflen_pre))
    msg = ct.create_string_buffer(buflen.contents.value)
    try:
        dll.kvaDbGetLastParseError(msg, buflen)
    except KvdBufferTooSmall:
        msg = ct.create_string_buffer(buflen.contents.value)
        dll.kvaDbGetLastParseError(msg, buflen)
    return msg.value.decode("utf-8")


_ct_dll = dllLoader.load_dll(win_name='kvaDbLib.dll', linux_name='libkvadblib.so')
dll = KvaDbDll(_ct_dll)
