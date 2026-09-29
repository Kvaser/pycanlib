from ..cenum import CEnum


# StatusERR
class Error(CEnum):
    OK = 0  #: OK
    FAIL = -1  #: Generic error
    ATTR_NOT_FOUND = -3  #: Failed to find an attribute in a node
    ATTR_VALUE = -4  #: The attribute value is not correct, e.g. whitespace after a number.
    ELEM_NOT_FOUND = -5  #: Could not find a required element
    VALUE_RANGE = -6  #: The value is outside the allowed range
    VALUE_UNIQUE = -7  #: The value is not unique; usually idx attributes
    VALUE_CONSECUTIVE = -8  #: The values are not consecutive; usually idx attributes
    POSTFIXEXPR = -9  #: The trigger expression could not be parsed
    XML_PARSER = -10  #: The XML settings contain syntax errors.
    DTD_VALIDATION = -11  #: The XML settings do not follow the DTD.
    SCRIPT_ERROR = -12  #: t-script related errors, e.g. file not found.
    INTERNAL = -20  #: Internal errors, e.g. null pointers.

    @classmethod
    def from_number(cls, number):
        """Create `Error` object from number.

        If the number is not defined in the class, return the number instead.
        This is used in order to be forward compatible with new codes in the dll.

        .. versionadded:: 1.19

        """
        try:
            return cls(number)
        except ValueError:
            return number


# ValidationError and ValidationWarning are the same enum
# (KvaXmlValidationStatus) in C.
class ValidationError(CEnum):
    OK = 0  #: OK
    FAIL = -1  #: Generic error.
    ABORT = -2  #: Too many errors, validation aborted.
    SILENT_TRANSMIT = -3  #: Transmit lists used in silent mode.
    UNDEFINED_TRIGGER = -4  #: An undefined trigger is used in an expression.
    MULTIPLE_EXT_TRIGGER = -5  #: There are more than one external trigger defined.
    MULTIPLE_START_TRIGGER = -6  #: There are more than one start up trigger defined.
    DISK_FULL_STARTS_LOG = -7  #: A trigger on disk full starts the logging.
    NUM_OUT_OF_RANGE = -8  #: A numerical value is out of range.
    SCRIPT_NOT_FOUND = -9  #: A t-script file could not be opened.
    SCRIPT_TOO_LARGE = -10  #: A t-script is too large for the configuration.
    SCRIPT_TOO_MANY = -11  #: Too many active t-scripts for selected device.
    SCRIPT_CONFLICT = -12  #: More than one active script is set as 'primary'.
    ELEMENT_COUNT = -13  #: Too many or too few elements of this type.
    PARSER = -14  #: A general error found during parsing.
    SCRIPT = -15  #: A general t-script error found during parsing.
    EXPRESSION = -16  #: A general trigger expression found during parsing.

    @classmethod
    def from_number(cls, number):
        """Create `ValidationError` object from number.

        If the number is not defined in the class, return the number instead.
        This is used in order to be forward compatible with new codes in the dll.

        .. versionadded:: 1.19

        """
        try:
            return cls(number)
        except ValueError:
            return number


class ValidationWarning(CEnum):
    ABORT = -100  #: Too many warnings, validation aborted.
    NO_ACTIVE_LOG = -101  #: No active logging detected.
    DISK_FULL_AND_FIFO = -102  #: A trigger on disk full used with FIFO mode.
    IGNORED_ELEMENT = -103  #: This XML element was ignored.
    MULTIPLE_EXT_TRIGGER = -104  #: Using more than one external trigger requires firmware version 3.7 or better.

    @classmethod
    def from_number(cls, number):
        """Create `ValidationWarning` from number.

        If the number is not defined in the class, return the number instead.
        This is used in order to be forward compatible with new codes in the dll.

        .. versionadded:: 1.19

        """
        try:
            return cls(number)
        except ValueError:
            return number
