from . import enums

# Most of these constants are deprecated, use the enum mentioned instead. (Or
# whatever is after the '=', even if its not an enum.)

kvlcOK = 0  # OK.
kvlcFail = enums.Error.FAIL
kvlcERR_PARAM = enums.Error.PARAM
kvlcEOF = enums.Error.EOF
kvlcERR_NOT_IMPLEMENTED = enums.Error.NOT_IMPLEMENTED
kvlcERR_FILE_ERROR = enums.Error.FILE_ERROR
kvlcERR_FILE_EXISTS = enums.Error.FILE_EXISTS
kvlcERR_INTERNAL_ERROR = enums.Error.INTERNAL_ERROR
kvlcERR_NULL_POINTER = enums.Error.NULL_POINTER
kvlcERR_FILE_TOO_LARGE = enums.Error.FILE_TOO_LARGE
kvlcERR_TYPE_MISMATCH = enums.Error.TYPE_MISMATCH
kvlcERR_NO_FREE_HANDLES = enums.Error.NO_FREE_HANDLES
# Missing call to kvlcSetInputFile or kvlcFeedSelectFormat.
kvlcERR_NO_INPUT_SELECTED = enums.Error.NO_INPUT_SELECTED
kvlcERR_CONVERTING = enums.Error.CONVERTING
kvlcERR_BUFFER_SIZE = enums.Error.BUFFER_SIZE
kvlcERR_INVALID_LOG_EVENT = enums.Error.INVALID_LOG_EVENT
kvlcERR_NO_TIME_REFERENCE = enums.Error.NO_TIME_REFERENCE
kvlcERR_TIME_DECREASING = enums.Error.TIME_DECREASING
kvlcERR_MIXED_ENDIANESS = enums.Error.MIXED_ENDIANESS

FILE_FORMAT_KME24 = enums.FileFormat.KME24
FILE_FORMAT_KME25 = enums.FileFormat.KME25
FILE_FORMAT_VECTOR_ASC = enums.FileFormat.VECTOR_ASC
FILE_FORMAT_CSV = enums.FileFormat.CSV
FILE_FORMAT_PLAIN_ASC = enums.FileFormat.PLAIN_ASC
FILE_FORMAT_MEMO_LOG = enums.FileFormat.MEMO_LOG
FILE_FORMAT_KME40 = enums.FileFormat.KME40
FILE_FORMAT_VECTOR_BLF = enums.FileFormat.VECTOR_BLF
FILE_FORMAT_VECTOR_BLF_FD = enums.FileFormat.VECTOR_BLF_FD
FILE_FORMAT_KME50 = enums.FileFormat.KME50
FILE_FORMAT_CSV_SIGNAL = enums.FileFormat.CSV_SIGNAL
FILE_FORMAT_MDF = enums.FileFormat.MDF
FILE_FORMAT_MATLAB = enums.FileFormat.MATLAB
FILE_FORMAT_J1587 = enums.FileFormat.J1587
FILE_FORMAT_J1587_ALT = enums.FileFormat.J1587_ALT
FILE_FORMAT_FAMOS = enums.FileFormat.FAMOS
FILE_FORMAT_MDF_SIGNAL = enums.FileFormat.MDF_SIGNAL
FILE_FORMAT_MDF_4X = enums.FileFormat.MDF_4X
FILE_FORMAT_MDF_4X_SIGNAL = enums.FileFormat.MDF_4X_SIGNAL
FILE_FORMAT_XCP = enums.FileFormat.XCP
FILE_FORMAT_FAMOS_XCP = enums.FileFormat.FAMOS_XCP
FILE_FORMAT_DEBUG = enums.FileFormat.DEBUG
