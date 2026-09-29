import ctypes as ct

from ..exceptions import DllException
from .constants import XML_ERROR_MESSAGE_LENGTH


def kva_error(status):
    """Create and return an exception object corresponding to `status`"""
    return KvaGeneralError(status)


class KvaError(DllException):
    """Base class for exceptions raised by the kvamemolibxml library

    Looks up the error text in the kvamemolibxml dll and presents it together with the
    error code.

    """
    @staticmethod
    def _get_error_text(status):
        try:
            from .wrapper import dll
        except ImportError:
            msg = "Unknown error text"
        else:
            try:
                msg_buf = ct.create_string_buffer(255)
                dll.kvaXmlGetErrorText(status, msg_buf, ct.sizeof(msg_buf))
                msg = msg_buf.value.decode('utf-8')
            # The important thing is to give original error code.
            except Exception:
                msg = "Unknown error text"
            try:
                msg_buf = ct.create_string_buffer(XML_ERROR_MESSAGE_LENGTH)
                dll.kvaXmlGetLastError(msg_buf, ct.sizeof(msg_buf), ct.byref(status))
                last = msg_buf.value.decode('utf-8')
            # The important thing is to give original error code.
            except Exception:
                last = ""

        msg += f' ({status})'
        if last:
            msg += '\n' + last

        return msg


class KvaGeneralError(KvaError):
    """A kvamemolibxml error that does not (yet) have its own Exception

    WARNING: Do not explicitly catch this error, instead catch `KvaError`. Your
    error may at any point in the future get its own exception class, and so
    will no longer be of this type. The actual status code that raised any
    `KvaError` can always be accessed through a `status` attribute.

    """

    def __init__(self, status):
        self.status = status
        super().__init__()
