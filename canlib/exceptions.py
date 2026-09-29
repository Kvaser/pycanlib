from . import deprecation


class CanlibException(Exception):
    """Base class for all exceptions in canlib"""

    pass


class DllException(CanlibException):
    """Base class for exceptions from dll calls in canlib

    All instances of this class must have a `status` attribute defined (this is
    enforced in the constructor). Its value is the status code that caused the
    exception.

    """

    @staticmethod
    def _get_error_text(status):
        return f"Unknown error text ({status})"

    def __init__(self):
        assert hasattr(self, 'status'), "DllExceptions must have a status attribute"
        super().__init__(self._get_error_text(self.status))

    canERR = deprecation.attr_replaced("canERR", "status")
