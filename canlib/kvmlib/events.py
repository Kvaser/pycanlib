import binascii
import ctypes as ct
import datetime
import sys
import time

from .. import canlib, frame
from ..exceptions import CanlibException


def _eq_or_none(a, b):
    return a == b or a is None or b is None


class LogEvent:
    """The base class for events recorded by a Memorator."""
    _comp_fields = None  # if not None, these attributes will be used to
    # compare objects

    def __init__(self, timestamp=None):
        self.timeStamp = timestamp
        self.ignored = False

    def __str__(self):
        if self.ignored:
            text = "*t:"
        else:
            text = " t:"
        if self.timeStamp is not None:
            text += "%14s " % (self.timeStamp / 1000000000.0)
        else:
            text += "             - "
        return text

    # In python 2, both __eq__ and __ne__ must be defined
    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        if not isinstance(other, LogEvent):
            return NotImplemented
        elif self._comp_fields is None:
            return NotImplemented
        elif self._comp_fields != other._comp_fields:
            return NotImplemented

        return all(
            _eq_or_none(getattr(self, name), getattr(other, name)) for name in self._comp_fields
        )


class MessageEvent(LogEvent):
    """A CAN message recorded by a Memorator"""

    _comp_fields = ('id', 'channel', 'dlc', 'flags', 'data', 'timeStamp')

    def __init__(self, id=None, channel=None, dlc=None, flags=None, data=None, timestamp=None):
        super().__init__(timestamp)
        self.id = id
        self.channel = channel
        self.dlc = dlc
        self.flags = flags
        if data is not None and not isinstance(data, (bytes, str)):
            if not isinstance(data, bytearray):
                data = bytearray(data)
            data = bytes(data)
        self.data = data
        if dlc is not None and data is not None:
            if len(data) > dlc:
                # dlc is (often) number of bytes
                self.data = data[:dlc]

    def asframe(self):
        """Convert this event to a `canlib.Frame`

        Creates a new `canlib.Frame` object with the same contents as this event.

        """
        return frame.Frame(
            id_=self.id,
            data=self.data,
            dlc=self.dlc,
            flags=canlib.MessageFlag(self.flags),
            timestamp=self.timeStamp,
        )

    def __str__(self):
        text = super().__str__()
        text += " ch:%s " % ("-" if self.channel is None else "%x" % self.channel)
        text += "f:%s " % (" -" if self.flags is None else "%5x" % self.flags)
        text += "id:%s " % ("   -" if self.id is None else "%4x" % self.id)
        text += "dlc:%s " % ("-" if self.dlc is None else "%2d" % self.dlc)
        if self.data is not None:
            data = self.data
            if not isinstance(data, (bytes, str)):
                if not isinstance(data, bytearray):
                    data = bytearray(data)
                data = bytes(data)
            try:
                hex = unicode(binascii.hexlify(data))
            except (NameError):
                hex = str(binascii.hexlify(data), 'ascii')
            formatted_data = ' '.join(hex[i:i + 2] for i in range(0, len(hex), 2))
            text += f"d:{formatted_data}"
        else:
            text += "d: -  -  -  -  -  -  -  -"
        return text

    def _asMrtEvent(self):
        """Convert this event to a `canlib.events.memoLogMrtEx`

        Creates a new `canlib.events.memoLogMrtEx` object with the same
        contents as this event.

        .. versionadded:: 1.7

        """
        # In python 2, *self.data returns a str
        if sys.version_info[0] < 3:
            data = (ct.c_ubyte * 64)(*bytearray(self.data))
        else:
            data = (ct.c_ubyte * 64)(*self.data)
        assert data == data
        msg = memoLogMsgEx(
            evType=memoLogEventEx.MEMOLOG_TYPE_MSG,
            id=self.id,
            timeStamp=self.timeStamp,
            channel=self.channel,
            dlc=self.dlc,
            flags=self.flags,
            data=data,
        )
        return memoLogMrtEx(msg=msg)


class RTCEvent(LogEvent):
    """An real-time clock message recorded by a Memorator"""

    _comp_fields = ('calendartime', 'timeStamp')

    def __init__(self, calendartime=None, timestamp=None):
        super().__init__(timestamp)
        self.calendartime = calendartime

    def __str__(self):
        text = super().__str__()
        text += " DateTime: %s" % self.calendartime
        return text

    def _asMrtEvent(self):
        """Convert this event to a `canlib.events.memoLogMrtEx`

        Creates a new `canlib.events.memoLogMrtEx` object with the same
        contents as this event.

        .. versionadded:: 1.7

        """
        # datetime.timestamp does not exist in Python 2.7
        try:
            calendar_time = int(self.calendartime.timestamp())  # only whole seconds
        except AttributeError:
            calendar_time = int(
                time.mktime(self.calendartime.timetuple())
                + self.calendartime.microsecond / 1000000.0
            )

        rtc = memoLogRtcClockEx(
            evType=memoLogEventEx.MEMOLOG_TYPE_CLOCK,
            calendarTime=calendar_time,
            timeStamp=self.timeStamp,
        )
        return memoLogMrtEx(rtc=rtc)


class TriggerEvent(LogEvent):
    """A trigger message recorded by a Memorator"""

    _comp_fields = ('type', 'timeStamp', 'pretrigger', 'posttrigger', 'trigno')

    def __init__(self, type=None, timestamp=None, pretrigger=None, posttrigger=None, trigno=None):
        super().__init__(timestamp)
        self.type = type
        self.pretrigger = pretrigger
        self.posttrigger = posttrigger
        self.trigno = trigno

    def __str__(self):
        text = super().__str__()
        text += "Log Trigger Event ("
        text += "type: 0x%x, " % (self.type)
        text += "trigno: 0x%02x, " % (self.trigno)
        text += "pre-trigger: %d, " % (self.pretrigger)
        text += "post-trigger: %d)\n" % (self.posttrigger)
        return text

    def _asMrtEvent(self):
        """Convert this event to a `canlib.events.memoLogMrtEx`

        Creates a new `canlib.events.memoLogMrtEx` object with the same
        contents as this event.

        .. versionadded:: 1.7

        """
        time_stamp_hi = self.timeStamp >> 32
        time_stamp_lo = self.timeStamp & 0xFFFFFFFF
        trig = memoLogTriggerEx(
            evType=memoLogEventEx.MEMOLOG_TYPE_TRIGGER,
            timeStampHi=time_stamp_hi,
            timeStampLo=time_stamp_lo,
            type=self.type,
            preTrigger=self.pretrigger,
            postTrigger=self.posttrigger,
            trigNo=self.trigno,
        )
        return memoLogMrtEx(trig=trig)


class VersionEvent(LogEvent):
    """A version message recorded by a Memorator"""

    _comp_fields = (
        'lioMajor',
        'lioMinor',
        'fwMajor',
        'fwMinor',
        'fwBuild',
        'serialNumber',
        'eanHi',
        'eanLo',
    )

    def __init__(self, lioMajor, lioMinor, fwMajor, fwMinor, fwBuild, serialNumber, eanHi, eanLo):
        super().__init__(None)
        self.lioMajor = lioMajor
        self.lioMinor = lioMinor
        self.fwMajor = fwMajor
        self.fwMinor = fwMinor
        self.fwBuild = fwBuild
        self.serialNumber = serialNumber
        self.eanHi = eanHi
        self.eanLo = eanLo
        self.ignored = True

    def __str__(self):
        text = super().__str__()
        text += "EAN:{:02x}-{:05x}-{:05x}-{:x}  ".format(
            self.eanHi >> 12,
            ((self.eanHi & 0xFFF) << 8) | (self.eanLo >> 24),
            (self.eanLo >> 4) & 0xFFFFF,
            self.eanLo & 0xF,
        )
        text += "s/n:%d  " % (self.serialNumber)
        text += f"FW:v{self.fwMajor}.{self.fwMinor}.{self.fwBuild}  "
        text += f"LIO:v{self.lioMajor}.{self.lioMinor}"
        return text

    def _asMrtEvent(self):
        """Convert this event to a `canlib.events.memoLogMrtEx`

        Creates a new `canlib.events.memoLogMrtEx` object with the same
        contents as this event.

        .. versionadded:: 1.7

        """
        ver = memoLogVersionEx(
            evType=memoLogEventEx.MEMOLOG_TYPE_VERSION,
            lioMajor=self.lioMajor,
            lioMinor=self.lioMinor,
            fwMajor=self.fwMajor,
            fwMinor=self.fwMinor,
            fwBuild=self.fwBuild,
            serialNumber=self.serialNumber,
            eanHi=self.eanHi,
            eanLo=self.eanLo,
        )
        return memoLogMrtEx(ver=ver)


####################################################################
# Low level ctypes classes for interacting with dll
class memoLogMsgEx(ct.Structure):
    _fields_ = [
        ('evType', ct.c_uint32),
        ('id', ct.c_uint32),  # The identifier
        ('timeStamp', ct.c_int64),  # timestamp in units of 1 nanoseconds
        # The channel on which the message arrived (0,1,...)
        ('channel', ct.c_uint32),
        ('dlc', ct.c_uint32),  # The length of the message
        ('flags', ct.c_uint32),  # Message flags
        ('data', ct.c_uint8 * 64),
    ]  # Message data (8 bytes)


class memoLogRtcClockEx(ct.Structure):
    _fields_ = [
        ('evType', ct.c_uint32),
        ('calendarTime', ct.c_uint32),  # RTC date (unix time format)
        ('timeStamp', ct.c_int64),
        ('padding', ct.c_uint8 * 24),
    ]


class memoLogTriggerEx(ct.Structure):
    _fields_ = [
        ('evType', ct.c_uint32),
        ('type', ct.c_int32),
        ('preTrigger', ct.c_int32),
        ('postTrigger', ct.c_int32),
        ('trigNo', ct.c_uint32),  # Bitmask with the activated trigger(s)
        # Timestamp in units of 1 nanoseconds; Can't use int64 here
        # since it is not naturally aligned
        ('timeStampLo', ct.c_uint32),
        ('timeStampHi', ct.c_uint32),
        ('padding', ct.c_uint8 * 8),
    ]


class memoLogVersionEx(ct.Structure):
    _fields_ = [
        ('evType', ct.c_uint32),
        ('lioMajor', ct.c_uint32),
        ('lioMinor', ct.c_uint32),
        ('fwMajor', ct.c_uint32),
        ('fwMinor', ct.c_uint32),
        ('fwBuild', ct.c_uint32),
        ('serialNumber', ct.c_uint32),
        ('eanHi', ct.c_uint32),
        ('eanLo', ct.c_uint32),
    ]


class memoLogRaw(ct.Structure):
    _fields_ = [('evType', ct.c_uint32), ('data', ct.c_uint8 * 32)]


class memoLogMrtEx(ct.Union):
    _fields_ = [
        ('msg', memoLogMsgEx),
        ('rtc', memoLogRtcClockEx),
        ('trig', memoLogTriggerEx),
        ('ver', memoLogVersionEx),
        ('raw', memoLogRaw),
    ]


class memoLogEventEx(ct.Structure):
    """Low level c type class holding a log event."""

    MEMOLOG_TYPE_INVALID = 0  #: Invalid MEMOLOG event type
    MEMOLOG_TYPE_CLOCK = 1  #: The event type used in kvmLogRtcClockEx
    MEMOLOG_TYPE_MSG = 2  #: The event type used in kvmLogMsgEx
    MEMOLOG_TYPE_TRIGGER = 3  #: The event type used in kvmLogTriggerEx
    MEMOLOG_TYPE_VERSION = 4  #: The event type used in kvmLogVersionEx

    _fields_ = [('event', memoLogMrtEx)]

    def createMemoEvent(self):
        """Convert event to `LogEvent`."""
        type = self.event.raw.evType

        if type == self.MEMOLOG_TYPE_CLOCK:
            cTime = self.event.rtc.calendarTime
            ct = datetime.datetime.fromtimestamp(cTime)
            memoEvent = RTCEvent(timestamp=self.event.rtc.timeStamp, calendartime=ct)

        elif type == self.MEMOLOG_TYPE_MSG:
            memoEvent = MessageEvent(
                timestamp=self.event.msg.timeStamp,
                id=self.event.msg.id,
                channel=self.event.msg.channel,
                dlc=self.event.msg.dlc,
                flags=self.event.msg.flags,
                data=self.event.msg.data,
            )

        elif type == self.MEMOLOG_TYPE_TRIGGER:
            tstamp = self.event.trig.timeStampLo + (self.event.trig.timeStampHi * 4294967296)
            memoEvent = TriggerEvent(
                timestamp=tstamp,
                type=self.event.trig.type,
                pretrigger=self.event.trig.preTrigger,
                posttrigger=self.event.trig.postTrigger,
                trigno=self.event.trig.trigNo,
            )

        elif type == self.MEMOLOG_TYPE_VERSION:
            memoEvent = VersionEvent(
                lioMajor=self.event.ver.lioMajor,
                lioMinor=self.event.ver.lioMinor,
                fwMajor=self.event.ver.fwMajor,
                fwMinor=self.event.ver.fwMinor,
                fwBuild=self.event.ver.fwBuild,
                serialNumber=self.event.ver.serialNumber,
                eanHi=self.event.ver.eanHi,
                eanLo=self.event.ver.eanLo,
            )
        else:
            raise CanlibException(f"createMemoEvent: Unknown event type :{type}")

        return memoEvent

    def __str__(self):
        type = self.event.raw.evType
        text = "Unkown type %d" % type

        if type == self.MEMOLOG_TYPE_CLOCK:
            cTime = self.event.rtc.calendarTime
            text = "t:%11f " % (self.event.rtc.timeStamp / 1000000000.0)
            text += "DateTime: %s (%d)" % (datetime.datetime.fromtimestamp(cTime), cTime)

        if type == self.MEMOLOG_TYPE_MSG:
            timestamp = self.event.msg.timeStamp
            channel = self.event.msg.channel
            flags = self.event.msg.flags
            dlc = self.event.msg.dlc
            id = self.event.msg.id
            data = self.event.msg.data[: frame.dlc_to_bytes(dlc, canFd=True)]
            dataString = " ".join(hex(c).split('x')[1] for c in data)
            text = "t:%11f ch:%x f:%5x id:%4x dlc:%2d d:%s" % (
                timestamp / 1000000000.0,
                channel,
                flags,
                id,
                dlc,
                dataString,
            )

        if type == self.MEMOLOG_TYPE_TRIGGER:
            # evType = self.event.trig.evType
            ttype = self.event.trig.type
            preTrigger = self.event.trig.preTrigger
            postTrigger = self.event.trig.postTrigger
            trigNo = self.event.trig.trigNo
            tstamp = self.event.trig.timeStampLo + (self.event.trig.timeStampHi * 4294967296)
            text = "t:%11f " % (tstamp / 1000000000.0)
            # text =  "t  : %11x\n" % (tstamp)
            # text += " et: %x (%x)\n" % (evType, type)
            text += "Log Trigger Event ("
            text += "type: 0x%x, " % (ttype)
            text += "trigNo: 0x%02x, " % (trigNo)
            text += "pre-trigger: %d, " % (preTrigger)
            text += "post-trigger: %d)" % (postTrigger)

        if type == self.MEMOLOG_TYPE_VERSION:
            lioMajor = self.event.ver.lioMajor
            lioMinor = self.event.ver.lioMinor
            fwMajor = self.event.ver.fwMajor
            fwMinor = self.event.ver.fwMinor
            fwBuild = self.event.ver.fwBuild
            serialNumber = self.event.ver.serialNumber
            eanHi = self.event.ver.eanHi
            eanLo = self.event.ver.eanLo
            text = "EAN:{:02x}-{:05x}-{:05x}-{:x}, ".format(
                eanHi >> 12,
                ((eanHi & 0xFFF) << 8) | (eanLo >> 24),
                (eanLo >> 4) & 0xFFFFF,
                eanLo & 0xF,
            )
            text += "S/N %d, " % serialNumber
            text += "FW v%d.%d.%d, " % (fwMajor, fwMinor, fwBuild)
            text += "LIO v%d.%d" % (lioMajor, lioMinor)
        return text
