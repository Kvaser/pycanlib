import ctypes as ct

from ..exceptions import DllException
from .enums import Error

_all_errors_by_status = {}


def _remember(cls):
    _all_errors_by_status[cls.status] = cls
    return cls


def kvd_error(status):
    """Create and return an exception object corresponding to `status`"""
    if status in _all_errors_by_status:
        return _all_errors_by_status[status]()
    else:
        return KvdGeneralError(status)


class KvdError(DllException):
    """Base class for exceptions raised by the kvadblib dll"""

    @staticmethod
    def _get_error_text(status):
        # Try the import locally so we don't trigger recursive calls to KvdError
        try:
            from .wrapper import dll

            msg = ct.create_string_buffer(80)
            dll.kvaDbGetErrorText(status, msg, ct.sizeof(msg))
            err_txt = msg.value.decode('utf-8')
        # The important thing is to give original error code.
        except Exception:
            err_txt = "Unknown error text"
        err_txt += f' ({status})'
        return err_txt


class KvdGeneralError(KvdError):
    """A kvadblib error that does not (yet) have its own Exception

    WARNING: Do not explicitly catch this error, instead catch `KvdError`. Your
    error may at any point in the future get its own exception class, and so
    will no longer be of this type. The actual status code that raised any
    `KvdError` can always be accessed through a `status` attribute.

    """

    def __init__(self, status):
        self.status = status
        super().__init__()


@_remember
class KvdBufferTooSmall(KvdError):
    """The buffer provided was not large enough to contain the requested data.

    .. versionadded:: 1.10

    """

    status = Error.BUFFER_TOO_SMALL


@_remember
class KvdDbFileParse(KvdError):
    """The database file could not be parsed.

    More information can be obtained by running `get_last_parse_error`.

    .. versionadded:: 1.10

    """

    status = Error.DB_FILE_PARSE


@_remember
class KvdErrInParameter(KvdError):
    """One or more of the parameters in call is erronous."""
    status = Error.PARAM


@_remember
class KvdInUse(KvdError):
    """An item is in use."""
    status = Error.IN_USE


class KvdNotFound(KvdError):
    pass


@_remember
class KvdNoAttribute(KvdNotFound):
    """No attribute found."""
    status = Error.NO_ATTRIB


@_remember
class KvdNoMessage(KvdNotFound):
    """No message was found."""
    status = Error.NO_MSG


@_remember
class KvdNoNode(KvdNotFound):
    """Could not find the database node."""
    status = Error.NO_NODE


@_remember
class KvdNoSignal(KvdNotFound):
    """No signal was found."""
    status = Error.NO_SIGNAL


@_remember
class KvdWrongOwner(KvdNotFound):
    """Wrong owner for attribute."""
    status = Error.WRONG_OWNER


@_remember
class KvdOnlyOneAllowed(KvdError):
    """An identical kvaDbLib structure already exists.

    Only one database at a time can be used).

    """
    status = Error.ONLY_ONE_ALLOWED
