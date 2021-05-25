from ..cenum import CEnum

# OK statuses are not included in any of these enums, as it is always the
# standard 0

# StatusERR
class Error(CEnum):
    FAIL = -1
    ATTR_NOT_FOUND = -3
    ATTR_VALUE = -4
    ELEM_NOT_FOUND = -5
    VALUE_RANGE = -6
    VALUE_UNIQUE = -7
    VALUE_CONSECUTIVE = -8
    POSTFIXEXPR = -9
    XML_PARSER = -10
    DTD_VALIDATION = -11
    SCRIPT_ERROR = -12
    INTERNAL = -20


# ValidationError and ValidationWarning are the same enum
# (KvaXmlValidationStatus) in C.


class ValidationError(CEnum):
    FAIL = -1
    ABORT = -2
    SILENT_TRANSMIT = -3
    UNDEFINED_TRIGGER = -4
    MULTIPLE_EXT_TRIGGER = -5
    MULTIPLE_START_TRIGGER = -6
    DISK_FULL_STARTS_LOG = -7
    NUM_OUT_OF_RANGE = -8
    SCRIPT_NOT_FOUND = -9
    SCRIPT_TOO_LARGE = -10
    SCRIPT_TOO_MANY = -11
    SCRIPT_CONFLICT = -12
    ELEMENT_COUNT = -13
    PARSER = -14
    SCRIPT = -15
    EXPRESSION = -16


class ValidationWarning(CEnum):
    ABORT = -100
    NO_ACTIVE_LOG = -101
    DISK_FULL_AND_FIFO = -102
    IGNORED_ELEMENT = -103
    MULTIPLE_EXT_TRIGGER = -104
