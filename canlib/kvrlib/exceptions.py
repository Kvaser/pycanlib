import ctypes as ct

from ..exceptions import DllException
from .enums import Error


def kvr_error(status):
    """Create and return an exception object corresponding to `status`"""
    for cls in (KvrBlank, KvrNoAnswer, KvrParameterError, KvrPasswordError, KvrUnreachable):
        if status == cls.status:
            return cls()
    else:
        return KvrGeneralError(status)


class KvrError(DllException):
    @staticmethod
    def _get_error_text(status):
        try:
            from .wrapper import dll

            msg = ct.create_string_buffer(80)
            dll.kvrGetErrorText(status, msg, ct.sizeof(msg))
            err_txt = msg.value.decode('utf-8')
        except:
            err_txt = "Unknown error text"

        err_txt += ' (%d)' % status
        return err_txt


class KvrGeneralError(KvrError):
    """A kvrlib error that does not (yet) have its own Exception

    WARNING: Do not explicitly catch this error, instead catch `KvrError`. Your
    error may at any point in the future get its own exception class, and so
    will no longer be of this type. The actual status code that raised any
    `KvrError` can always be accessed through a `status` attribute.

    """

    def __init__(self, status):
        self.status = status
        super(KvrGeneralError, self).__init__()


class KvrBlank(KvrError):
    status = Error.BLANK


class KvrNoAnswer(KvrError):
    status = Error.NO_ANSWER


class KvrParameterError(KvrError):
    status = Error.PARAMETER


class KvrPasswordError(KvrError):
    status = Error.PASSWORD


class KvrUnreachable(KvrError):
    status = Error.NO_DEVICE
