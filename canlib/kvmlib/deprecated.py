import ctypes as ct
import datetime
import os
import time

from .. import deprecation
from . import constants as const
from .enums import FileType
from .events import memoLogEventEx
from .exceptions import KvmNoLogMsg, kvm_error
from .wrapper import dll


class kvmVersion:
    """
    Class that holds kvmlib version number.

    """

    def __init__(self, major, minor, build):
        self.major = major
        self.minor = minor
        self.build = build

    def __str__(self):
        """
        Presents the version number as 'major.minor.build'.
        """
        return "%d.%d.%d" % (self.major, self.minor, self.build)


class KvmLib:
    """Deprecated wrapper class for the Kvaser kvmlib.

    .. deprecated:: 1.6

    All functionality has been moved to the kvmlib module itself.

      # deprecated
      from canlib import kvmlib
      cl = kvmlib.kvmlib()
      cl.functionName()

      # use this instead
      from canlib import kvmlib
      kvmlib.functionName()

    This class wraps the Kvaser kvmlib dll. For more info, see the kvmlib help
    files which are availible in the CANlib SDK.
    https://www.kvaser.com/developer/canlib-sdk/

    """

    dll = dll

    def __init__(self):
        deprecation.manual_warn(
            "Creating KvmLib objects is deprecated, "
            "all functionality has been moved to the kvmlib module itself."
        )
        self.handle = None
        self.kmeHandle = None
        self.logFileIndex = None
        self.dll.kvmInitialize()

    def getVersion(self):
        """Get the kvmlib version number.

        Returns the kvmlib version number from the kvmlib DLL currently in use.

        .. deprecated:: 1.5
           Use `dllversion` instead.

        Args:
            None

        Returns:
            version (kvmVersion): Major and minor version number

        """
        major = ct.c_int()
        minor = ct.c_int()
        build = ct.c_int()
        self.dll.kvmGetVersion(ct.byref(major), ct.byref(minor), ct.byref(build))
        version = kvmVersion(major.value, minor.value, build.value)
        return version

    @deprecation.deprecated.favour("deviceOpen")
    def openDeviceEx(self, memoNr=0, devicetype=const.kvmDEVICE_MHYDRA):
        """Deprecated function

        .. deprecated:: 1.5
           Use `deviceOpen` instead.

        """
        self.deviceOpen(memoNr, devicetype)

    def deviceOpen(self, memoNr=0, devicetype=const.kvmDEVICE_MHYDRA):
        status_p = ct.c_int()
        self.handle = self.dll.kvmDeviceOpen(memoNr, ct.byref(status_p), devicetype)

    @deprecation.deprecated.favour("deviceMountKmf")
    def openLog(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `deviceMountKmf` instead.

        """
        self.deviceMountKmf()

    def deviceMountKmf(self):
        """Mount device log files (kmf)

        Mount the log area on the SD card on a connected Kvaser Memorator and
        return the logger data format (LDF) version.

        Returns:
            ldfVersion (str): The logger data format (e.g. '5.0')

        """
        ldfMajor = ct.c_int(0)
        ldfMinor = ct.c_int(0)
        self.dll.kvmDeviceMountKmfEx(self.handle, ldfMajor, ldfMinor)
        return "%d.%d" % (ldfMajor.value, ldfMinor.value)

    @deprecation.deprecated.favour("kmfReadConfig")
    def readConfig(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `kmfReadConfig` instead.

        """
        self.kmfReadConfig()

    def kmfReadConfig(self):
        lif_buf = ct.create_string_buffer(320 * 32 * 1024)
        actual_len = ct.c_size_t(0)
        self.dll.kvmKmfReadConfig(
            self.handle, ct.byref(lif_buf), ct.sizeof(lif_buf), ct.byref(actual_len)
        )
        return lif_buf.raw[: actual_len.value]

    @deprecation.deprecated.favour("kmfGetUsage")
    def getFileSystemUsage(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `kmfGetUsage` instead.

        """
        self.kmfGetUsage()

    def kmfGetUsage(self):
        totalSectorCount = ct.c_uint32()
        usedSectorCount = ct.c_uint32()
        self.dll.kvmKmfGetUsage(self.handle, ct.byref(totalSectorCount), ct.byref(usedSectorCount))
        return (
            int((totalSectorCount.value * 512) / (1000 * 1000)),
            int((usedSectorCount.value * 512) / (1000 * 1000)),
        )

    def kmfOpen(self, filename, deviceType=const.kvmDEVICE_MHYDRA):
        status_p = ct.c_int()
        self.handle = self.dll.kvmKmfOpen(filename.encode(), ct.byref(status_p), deviceType)
        if status_p.value < 0:
            self.handle = None
            print("ERROR filename:%s, devicetype:%d\n" % (filename, deviceType))
            raise kvm_error(status_p.value)

    def kmfOpenEx(self, filename, deviceType=const.kvmDEVICE_MHYDRA):
        status_p = ct.c_int()
        ldfMajor = ct.c_int()
        ldfMinor = ct.c_int()
        self.handle = self.dll.kvmKmfOpenEx(
            filename.encode(),
            ct.byref(status_p),
            deviceType,
            ct.byref(ldfMajor),
            ct.byref(ldfMinor),
        )
        if status_p.value < 0:
            self.handle = None
            print("ERROR filename:%s, devicetype:%d\n" % (filename, deviceType))
            raise kvm_error(status_p.value)
        return "%d.%d" % (ldfMajor.value, ldfMinor.value)

    @deprecation.deprecated.favour("deviceGetDiskSize")
    def getDiskSize(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `deviceGetDiskSize` instead.

        """
        self.deviceGetDiskSize()

    def deviceGetDiskSize(self):
        diskSize = ct.c_uint32()
        self.dll.kvmDeviceDiskSize(self.handle, ct.byref(diskSize))
        return int((diskSize.value * 512) / (1000 * 1000))

    def logFileGetStartTime(self):
        startTime = ct.c_uint32()
        self.dll.kvmLogFileGetStartTime(self.handle, ct.byref(startTime))
        return datetime.datetime.fromtimestamp(startTime.value)

    @deprecation.deprecated.favour("deviceGetRTC")
    def getRTC(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `deviceGetRTC` instead.

        """
        self.deviceGetRTC()

    def deviceGetRTC(self):
        time = ct.c_uint32()
        self.dll.kvmDeviceGetRTC(self.handle, ct.byref(time))
        return datetime.datetime.fromtimestamp(time.value)

    @deprecation.deprecated.favour("deviceSetRTC")
    def setRTC(self, timestamp):
        """Deprecated function

        .. deprecated:: 1.5
           Use `deviceSetRTC` instead.

        """
        self.deviceSetRTC(timestamp)

    def deviceSetRTC(self, timestamp):
        unixTime = ct.c_uint32(int(time.mktime(timestamp.timetuple())))
        self.dll.kvmDeviceSetRTC(self.handle, unixTime)

    @deprecation.deprecated.favour("deviceGetDiskStatus")
    def isDiskPresent(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `deviceGetDiskStatus` instead.

        """
        self.deviceGetDiskStatus()

    def deviceGetDiskStatus(self):
        present = ct.c_int(0)
        self.dll.kvmDeviceDiskStatus(self.handle, ct.byref(present))
        return not (present.value == 0)

    @deprecation.deprecated.favour("logFileGetCount")
    def getLogFileCount(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `logFileGetCount` instead.

        """
        self.logFileGetCount()

    def logFileGetCount(self):
        fileCount = ct.c_uint32()
        self.dll.kvmLogFileGetCount(self.handle, ct.byref(fileCount))
        return fileCount.value

    @deprecation.deprecated.favour("deviceGetSerialNumber")
    def getSerialNumber(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `deviceGetSerialNumber` instead.

        """
        self.deviceGetSerialNumber()

    def deviceGetSerialNumber(self):
        serial = ct.c_uint()
        self.dll.kvmDeviceGetSerialNumber(self.handle, ct.byref(serial))
        return serial.value

    @deprecation.deprecated.favour("logFileDismount")
    def logCloseFile(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `logFileDismount` instead.

        """
        self.logFileDismount()

    def logFileDismount(self):
        self.dll.kvmLogFileDismount(self.handle)
        self.logFileIndex = None
        self.eventCount = 0

    @deprecation.deprecated.favour("logFileMount")
    def logOpenFile(self, fileIndx):
        """Deprecated function

        .. deprecated:: 1.5
           Use `logFileMount` instead.

        """
        self.logFileMount(fileIndx)

    @deprecation.deprecated.favour("Memorator.mount")
    def logFileMount(self, fileIndx):
        """Deprecated function

        .. deprecated:: 1.5
           Use `.Memorator.mount` instead.

        """
        if self.logFileIndex is not None:
            self.logFileDismount
        eventCount = ct.c_uint32()
        self.dll.kvmLogFileMount(self.handle, fileIndx, ct.byref(eventCount))
        self.logFileIndex = fileIndx
        self.eventCount = eventCount.value
        self.events = []
        return self.eventCount

    @deprecation.deprecated.favour("logFileReadEvent")
    def logReadEventEx(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `logFileReadEvent` instead.

        """
        self.logFileReadEvent()

    def logFileReadEvent(self):
        logevent = memoLogEventEx()
        try:
            self.dll.kvmLogFileReadEvent(self.handle, ct.byref(logevent))
        except (KvmNoLogMsg):
            return None
        memoEvent = logevent.createMemoEvent()
        return memoEvent

    def logFileReadEventLogFormat(self):
        logevent = memoLogEventEx()
        try:
            self.dll.kvmLogFileReadEvent(self.handle, ct.byref(logevent))
        except (KvmNoLogMsg):
            return None
        return logevent

    @deprecation.deprecated.favour("Kme50.read_event")
    def kmeReadEvent(self):
        logevent = memoLogEventEx()
        try:
            self.dll.kvmKmeReadEvent(self.kmeHandle, logevent)
        except (KvmNoLogMsg):
            return None
        hexstring = ''.join([f'{b:02x}' for b in logevent.event.raw.data])
        n = 4
        grouped_hexstring = [hexstring[i:i + n] for i in range(0, len(hexstring), n)]
        print('Read Dr event:', ' '.join(grouped_hexstring))
        memoEvent = logevent.createMemoEvent()
        return memoEvent

    @deprecation.deprecated.favour("Kme.read_event")
    def kmeReadEventLogFormat(self):
        logevent = memoLogEventEx()
        try:
            self.dll.kvmKmeReadEvent(self.kmeHandle, ct.byref(logevent))
        except (KvmNoLogMsg):
            return None
        return logevent

    @deprecation.deprecated.favour("Kme50.write_event")
    def kmeWriteEvent(self, logevent):
        self.dll.kvmKmeWriteEvent(self.kmeHandle, logevent)

    @deprecation.deprecated.favour("logFileReadEvents")
    def readEvents(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `logFileReadEvents` instead.

        """
        return self.logFileReadEvents()

    @deprecation.deprecated.favour("logFileReadEvents")
    def logReadEvents(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `logFileReadEvents` instead.

        """
        self.logFileReadEvents()

    def logFileReadEvents(self):
        while True:
            event = self.logFileReadEvent()
            if event is None:
                break
            self.events.append(event)
        return self.events

    @deprecation.deprecated.favour("kmfValidate")
    def validateDisk(self, fix=0):
        """Deprecated function

        .. deprecated:: 1.5
           Use `kmfValidate` instead.

        """
        self.kmfValidate(fix)

    def kmfValidate(self, fix=0):
        self.dll.kvmKmfValidate(self.handle)

    @deprecation.deprecated.favour("kmfWriteConfig")
    def writeConfigLif(self, lifData):
        """writeConfig

        .. deprecated:: 1.5
           Use `kmfWriteConfig` instead.

        """
        self.kmfWriteConfig(lifData)

    def kmfWriteConfig(self, lifData):
        buf = ct.create_string_buffer(lifData)
        self.dll.kvmKmfWriteConfig(self.handle, ct.byref(buf), len(lifData))

    def logFileDeleteAll(self):
        self.dll.kvmLogFileDeleteAll(self.handle)

    def writeConfig(self, config):
        self.kmfWriteConfig(config.toLif())

    @deprecation.deprecated.favour("deviceFormatDisk")
    def formatDisk(self, reserveSpace=10, dbaseSpace=2, fat32=True):
        """Deprecated function

        .. deprecated:: 1.5
           Use `deviceFormatDisk` instead.

        """
        self.deviceFormatDisk(reserveSpace, dbaseSpace, fat32)

    def deviceFormatDisk(self, reserveSpace=10, dbaseSpace=2, fat32=True):
        return self.dll.kvmDeviceFormatDisk(self.handle, fat32, reserveSpace, dbaseSpace)

    @deprecation.deprecated.favour("close")
    def closeDevice(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `close` instead.

        """
        self.close()

    def close(self):
        self.dll.kvmClose(self.handle)
        self.handle = None

    @deprecation.deprecated.favour("kvmlib.openKme")
    def kmeOpenFile(self, filename, filetype=FileType.KME40):
        if self.kmeHandle is not None:
            self.kmeCloseFile()
        status_p = ct.c_int32()
        self.kmeHandle = self.dll.kvmKmeOpenFile(filename.encode(), ct.byref(status_p), filetype)
        if status_p.value != 0:
            self.kmeHandle = None
            print(
                "ERROR kmeOpenFile failed with filename:"
                "%s, filetype:%s\n" % (filename, filetype)
            )
            raise kvm_error(status_p.value)

    @deprecation.deprecated.favour("kvmlib.kme_file_type")
    def kmeScanFileType(self, filename):
        """Scan KME file and report version

        Open and read the file filename and try to decode what version
        of KME it contains. Returns type as kvmFILE_xxx.
        """
        type = ct.c_int32()
        filename = os.path.realpath(filename)
        ct_filename = ct.c_char_p(filename.encode())
        self.dll.kvmKmeScanFileType(ct_filename, ct.byref(type))
        return type.value

    @deprecation.deprecated.favour("kvmlib.createKme")
    def kmeCreateFile(self, filename, filetype=FileType.KME40):
        if self.kmeHandle is not None:
            self.kmeCloseFile()
        status_p = ct.c_int32()
        ct_filename = ct.c_char_p(filename.encode())
        self.kmeHandle = self.dll.kvmKmeCreateFile(ct_filename, ct.byref(status_p), filetype)
        if status_p.value != 0:
            self.kmeHandle = None
            print(
                "ERROR kmeCreateFile failed with filename:"
                "%s, filetype:%s\n" % (filename, filetype)
            )
            raise kvm_error(status_p.value)

    @deprecation.deprecated.favour("Kme.estimate_events")
    def kmeCountEvents(self):
        eventCount = ct.c_uint32(0)
        self.dll.kvmKmeCountEvents(self.kmeHandle, ct.byref(eventCount))
        return eventCount.value

    @deprecation.deprecated.favour("Kme.close")
    def kmeCloseFile(self):
        self.dll.kvmKmeCloseFile(self.kmeHandle)
        self.kmeHandle = None
