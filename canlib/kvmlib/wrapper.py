import ctypes as ct

from .. import VersionNumber, dllLoader
from .dll import KvmlibDll

_ct_dll = dllLoader.load_dll(win_name='kvmlib.dll', linux_name='libkvmlib.so')
dll = KvmlibDll(_ct_dll)
dll.kvmInitialize()


def dllversion():
    """Get the kvmlib version number as a `canlib.VersionNumber`"""
    major = ct.c_int()
    minor = ct.c_int()
    build = ct.c_int()
    dll.kvmGetVersion(ct.byref(major), ct.byref(minor), ct.byref(build))
    version = VersionNumber(major.value, minor.value, build.value)
    return version
