from ..exceptions import DllException
from .enums import Error

error_text = {
    Error.NOMSG: "No messages available.",
    Error.NOTRUNNING: "NOTRUNNING",
    Error.RUNNING: "RUNNING",
    Error.MASTERONLY: "MASTERONLY",
    Error.SLAVEONLY: "SLAVEONLY",
    Error.PARAM: "Error in parameter.",
    Error.NOTFOUND: "Specified hardware not found. This error is reported when the LIN transceiver isn't powered up.",
    Error.NOMEM: "Out of memory.",
    Error.NOCHANNELS: "No channels avaliable.",
    Error.TIMEOUT: "Timeout occurred.",
    Error.NOTINITIALIZED: "Library not initialized.",
    Error.NOHANDLES: "Can't get handle.",
    Error.INVHANDLE: "Handle is invalid.",
    Error.CANERROR: "CANERROR",
    Error.ERRRESP: "There was an error response from the LIN interface.",
    Error.WRONGRESP: "The LIN interface response wasn't the expected one.",
    Error.DRIVER: "CAN driver type not supported.",
    Error.DRIVERFAILED: "DeviceIOControl failed.",
    Error.NOCARD: "The card was removed or not inserted.",
    Error.LICENSE: "The license is not valid.",
    Error.INTERNAL: "Internal error in the driver.",
    Error.NO_ACCESS: "Access denied.",
    Error.VERSION: "Function not supported in this version.",
    Error.NO_REF_POWER: "Function not supported in this version.",
    Error.NOT_IMPLEMENTED: "Requested feature/function not implemented in the device.",
}


def lin_error(status):
    """Create and return an exception object corresponding to `status`"""
    if status == Error.NOMSG:
        return LinNoMessageError()
    if status == Error.NOT_IMPLEMENTED:
        return LinNotImplementedError()
    else:
        return LinGeneralError(status)


class LinError(DllException):
    """Base class for exceptions raised by the linlib class

    Looks up the error text in the linlib dll and presents it together with the
    error code and the wrapper function that triggered the exception.

    """

    @staticmethod
    def _get_error_text(status):
        msg = error_text.get(status, None) or "Unknown error text"
        msg += f' ({status})'
        return msg


class LinGeneralError(LinError):
    """A linlib error that does not (yet) have its own Exception

    .. warning:: Do not explicitly catch this error, instead catch `LinError`. Your
        error may at any point in the future get its own exception class, and
        so will no longer be of this type. The actual status code that raised
        any `LinError` can always be accessed through a `status` attribute.

    """

    def __init__(self, status):
        self.status = status
        super().__init__()


class LinNoMessageError(LinError):
    """No messages where availible"""

    status = Error.NOMSG


class LinNotImplementedError(LinError):
    """Feature/function not implemented in the device"""

    status = Error.NOT_IMPLEMENTED
