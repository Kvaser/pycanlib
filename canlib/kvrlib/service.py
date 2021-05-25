import ctypes as ct

from .wrapper import dll


def query():
    status = ct.c_int()
    dll.kvrServiceQuery(ct.byref(status))
    return status.value


def start():
    status = ct.c_int()
    dll.kvrServiceStart(ct.byref(status))
    return status.value


def stop():
    status = ct.c_int()
    dll.kvrServiceStop(ct.byref(status))
    return status.value
