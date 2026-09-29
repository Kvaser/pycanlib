"""Wrapper for the Kvaser kvmlib library

The kvmlib is used to interact with Kvaser Memorator devices that can record
CAN messages (E.g. Kvaser Memorator Professional 5xHS). You can download
configuration data (e.g. triggers, filters, scripts) allowing you to disconnect
the device from your computer, connect the device to a CAN bus and let it
record the traffic autonomously. When done, you can reconnect the device with
your computer and use kvmlib to get the recorded data.

"""

from ..frame import dlc_to_bytes
from .constants import *
from .deprecated import KvmLib as kvmlib  # for backwards-compatibility
from .enums import Device, Error, FileType, LoggerDataFormat
from .events import (LogEvent, MessageEvent, RTCEvent, TriggerEvent,
                     VersionEvent, memoLogEventEx, memoLogMrtEx, memoLogMsgEx,
                     memoLogRaw, memoLogRtcClockEx, memoLogTriggerEx,
                     memoLogVersionEx)
from .exceptions import (
    KvmDiskError, KvmDiskNotFormated, KvmError, KvmNoDisk, KvmNoLogMsg,
    LockedLogError)
from .kme import Kme, createKme, kme_file_type, openKme
from .kmf import Kmf, KmfSystem, openKmf
from .log import MountedLog, UnmountedLog
from .logfile import LogFile
from .memorator import Memorator, openDevice
from .messages import (logMsg, memoMsg, rtcMsg, trigMsg,  # Deprecated classes
                       verMsg)
from .wrapper import dllversion

kvmError = KvmError
kvmDiskError = KvmDiskError
kvmNoDisk = KvmNoDisk
kvmDiskNotFormated = KvmDiskNotFormated
kvmNoLogMsg = KvmNoLogMsg
