import ctypes as ct

from .wrapper import dll


def query():
    """Queries the status of the helper service.

    The helper service is installed as a part of the Windows CANlib driver
    package and is normally set to automatic start.

    """
    status = ct.c_int()
    dll.kvrServiceQuery(ct.byref(status))
    return status.value


def start():
    """Start the helper service.

    The helper service is installed as a part of the Windows CANlib driver
    package and is normally set to automatic start.

    """
    status = ct.c_int()
    dll.kvrServiceStart(ct.byref(status))
    return status.value


def stop():
    """Stop the helper service.

    The helper service is installed as a part of the Windows CANlib driver
    package and is normally set to automatic start.

    """
    status = ct.c_int()
    dll.kvrServiceStop(ct.byref(status))
    return status.value
