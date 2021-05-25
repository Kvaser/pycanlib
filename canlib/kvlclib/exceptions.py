import ctypes as ct

from ..exceptions import DllException
from .enums import Error


def kvlc_error(status):
    """Create and return an exception object corresponding to `status`"""
    if status == KvlcEndOfFile.status:
        return KvlcEndOfFile()
    elif status == KvlcNotImplemented.status:
        return KvlcNotImplemented()
    elif status == KvlcFileExists.status:
        return KvlcFileExists()
    else:
        return KvlcGeneralError(status)


class KvlcError(DllException):
    """Base class for exceptions raised by the Kvlclib class.

    Looks up the error text in the kvlclib dll and presents it together with
    the error code and the wrapper function that triggered the exception.

    """

    @staticmethod
    def _get_error_text(status):
        try:
            from .wrapper import dll

            msg = ct.create_string_buffer("Error description is missing.".encode('utf-8'))
            dll.kvlcGetErrorText(status, msg, ct.sizeof(msg))
            err_txt = msg.value.decode('utf-8')
        except:
            err_txt = "Unknown error text"
        return err_txt + ' (%d)' % status


class KvlcGeneralError(KvlcError):
    """A kvlclib error that does not (yet) have its own Exception

    WARNING: Do not explicitly catch this error, instead catch `KvlcError`. Your
    error may at any point in the future get its own exception class, and so
    will no longer be of this type. The actual status code that raised any
    `KvlcError` can always be accessed through a `status` attribute.

    """

    def __init__(self, status):
        self.status = status
        super(KvlcGeneralError, self).__init__()


class KvlcEndOfFile(KvlcError):
    """Exception used when EOF is reached on input file."""

    status = Error.EOF


class KvlcFileExists(KvlcError):
    """File exists, set `Property.OVERWRITE` to overwrite

    .. versionadded:: 1.17
    """

    status = Error.FILE_EXISTS


class KvlcNotImplemented(KvlcError, NotImplementedError):
    """Exception used when kvlclib returns -11."""

    status = Error.NOT_IMPLEMENTED
