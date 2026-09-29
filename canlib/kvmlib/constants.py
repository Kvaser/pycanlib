from . import enums

# Most of these constants are deprecated, use the enum mentioned instead. (Or
# whatever is after the '=', even if its not an enum.)

kvmOK = 0
kvmFail = enums.Error.FAIL
kvmERR_PARAM = enums.Error.PARAM
kvmERR_LOGFILEOPEN = enums.Error.LOGFILEOPEN
kvmERR_NOSTARTTIME = enums.Error.NOSTARTTIME
kvmERR_NOLOGMSG = enums.Error.NOLOGMSG
kvmERR_LOGFILEWRITE = enums.Error.LOGFILEWRITE
kvmEOF = enums.Error.FAIL
kvmERR_NO_DISK = enums.Error.NO_DISK
kvmERR_LOGFILEREAD = enums.Error.LOGFILEREAD

kvmERR_QUEUE_FULL = enums.Error.QUEUE_FULL
kvmERR_CRC_ERROR = enums.Error.CRC_ERROR
kvmERR_SECTOR_ERASED = enums.Error.SECTOR_ERASED
kvmERR_FILE_ERROR = enums.Error.FILE_ERROR
kvmERR_DISK_ERROR = enums.Error.DISK_ERROR
kvmERR_DISKFULL_DIR = enums.Error.DISKFULL_DIR
kvmERR_DISKFULL_DATA = enums.Error.DISKFULL_DATA
kvmERR_SEQ_ERROR = enums.Error.SEQ_ERROR
kvmERR_FILE_SYSTEM_CORRUPT = enums.Error.FILE_SYSTEM_CORRUPT
kvmERR_UNSUPPORTED_VERSION = enums.Error.UNSUPPORTED_VERSION
kvmERR_NOT_IMPLEMENTED = enums.Error.NOT_IMPLEMENTED
kvmERR_FATAL_ERROR = enums.Error.FATAL_ERROR
kvmERR_ILLEGAL_REQUEST = enums.Error.ILLEGAL_REQUEST
kvmERR_FILE_NOT_FOUND = enums.Error.FILE_NOT_FOUND
kvmERR_NOT_FORMATTED = enums.Error.NOT_FORMATTED
kvmERR_WRONG_DISK_TYPE = enums.Error.WRONG_DISK_TYPE
kvmERR_TIMEOUT = enums.Error.TIMEOUT
kvmERR_DEVICE_COMM_ERROR = enums.Error.DEVICE_COMM_ERROR
kvmERR_OCCUPIED = enums.Error.OCCUPIED
kvmERR_USER_CANCEL = enums.Error.USER_CANCEL
kvmERR_FIRMWARE = enums.Error.FIRMWARE
kvmERR_CONFIG_ERROR = enums.Error.CONFIG_ERROR
kvmERR_WRITE_PROT = enums.Error.WRITE_PROT

kvmDEVICE_MHYDRA = enums.Device.MHYDRA
kvmDEVICE_MHYDRA_EXT = enums.Device.MHYDRA_EXT

kvmFILE_KME24 = enums.FileType.KME24
kvmFILE_KME25 = enums.FileType.KME25
kvmFILE_KME40 = enums.FileType.KME40
kvmFILE_KME50 = enums.FileType.KME50

kvmLDF_MAJOR_CAN = enums.LoggerDataFormat.MAJOR_CAN  # Used in Kvaser Memorator
# (2nd generation)
kvmLDF_MAJOR_CAN64 = enums.LoggerDataFormat.MAJOR_CAN64  # Used in Kvaser
# Memorator (2nd generation) with extended data capabilities.
