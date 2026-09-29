import ctypes as ct

from ..exceptions import DllException
from .enums import Error


class LockedLogError(RuntimeError):
    """Raised when trying to mount a log file to a locked log

    Only one log file can be "mounted" internally at time. When a `LogFile`
    object requires its log file to be kept mounted for an extended period of
    time (such as when iterating over it) it will lock its containing
    `MountedLog` object. If during this time an attempt is made to mount a log
    file, this error will be raised.

    """

    def __init__(self):
        super().__init__("Active log file switched during iteration")


_all_errors_by_status = {}


def _remember(cls):
    _all_errors_by_status[cls.status] = cls
    return cls


def kvm_error(status):
    """Create and return an exception object corresponding to `status`"""
    if status in _all_errors_by_status:
        return _all_errors_by_status[status]()
    else:
        return KvmGeneralError(status)


class KvmError(DllException):
    """Base class for exceptions raised by the kvmlib dll"""

    @staticmethod
    def _get_error_text(status):
        # Try the import locally so we don't trigger recursive calls to KvdError
        try:
            from .wrapper import dll

            msg = ct.create_string_buffer(80)
            dll.kvmGetErrorText(status, msg, ct.sizeof(msg))
            err_txt = msg.value.decode('utf-8')
        # The important thing is to give original error code.
        except Exception:
            err_txt = "Unknown error text"
        err_txt += f' ({status})'
        return err_txt


class KvmGeneralError(KvmError):
    """A kvmlib error that does not (yet) have its own Exception

    WARNING: Do not explicitly catch this error, instead catch `KvmError`. Your
    error may at any point in the future get its own exception class, and so
    will no longer be of this type. The actual status code that raised any
    `KvmError` can always be accessed through a `status` attribute.

    """

    def __init__(self, status):
        self.status = status
        super().__init__()


@_remember
class KvmDiskError(KvmError):
    """General disk error"""

    status = Error.DISK_ERROR


@_remember
class KvmNoDisk(KvmDiskError):
    """No disk found"""

    status = Error.NO_DISK


@_remember
class KvmDiskNotFormated(KvmDiskError):
    """Disk not formatted"""

    status = Error.NOT_FORMATTED


@_remember
class KvmNoLogMsg(KvmError):
    """No log message found"""

    status = Error.NOLOGMSG
