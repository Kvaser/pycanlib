import ctypes as ct
import datetime
from functools import wraps

from .enums import LogFileType
from .events import memoLogEventEx
from .exceptions import KvmNoLogMsg
from .wrapper import dll


class LogFile:
    """A log file read from a `MountedLog` object

    This class is normally not directly instantiated but retrieved from a
    `MountedLog` object.

    The most common use of this class is iterating through it to get the
    individual events as `LogEvent` subclasses::

        for event in logfile:
            ...

    Note:

        While iterating over a `LogFile`, accessing any other `LogFile` is will
        result in a `LockedLogError`. Make sure to finish the loop (or when
        using iteration objects directly call the `close` method) before
        interacting with any other log files.

    A fast approximation of the number of events is given by
    `event_count_estimation`, the exact number of events can be calculated
    using::

        num_events = len(list(logfile))

    Finally this class has several read-only properties for getting information
    about the log file itself.

    Note:
        Before any data is fetched from the dll, this class will make sure that
        the correct file has been mounted on the underlying ``kvmHandle``.

        Manually mounting or unmounting log files by calling the dll directly
        is not supported.

    .. versionadded:: 1.6

    """

    def _mounted_handle(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cont = self._container
            if cont._mounted_index != self.index:
                self._remount()
            return func(self, cont.handle, *args, **kwargs)

        return wrapper

    def __init__(self, container, index):
        self._container = container
        self.index = index

    def __iter__(self):
        # force a remount, to reset the dll's internal event counter
        self._remount()

        try:
            self._container._mount_lock = True
            while True:
                # It is currently up to the user to make sure the handle/device
                # stays mounted on this file during iteration.
                eventstruct = memoLogEventEx()
                dll.kvmLogFileReadEvent(self._container.handle, ct.byref(eventstruct))
                event = eventstruct.createMemoEvent()
                yield event
        except (KvmNoLogMsg, GeneratorExit):
            # GeneratorExit is raised when close() is called on this
            # generator. This means that if we iterate over the LogFile
            # manually (it = iter(LogFile) and then next(it)) we can also
            # release the lock when we close it (it.close())
            self._container._mount_lock = False
            return

    @property
    @_mounted_handle
    def creator_serial(self, handle):
        """`int`: The serial number of the interface that created the log file"""
        serial = ct.c_uint32()
        dll.kvmLogFileGetCreatorSerial(handle, ct.byref(serial))
        return serial.value

    @property
    @_mounted_handle
    def end_time(self, handle):
        """`datetime.datetime`: The time of the last event in the log file"""
        time = ct.c_uint32()
        dll.kvmLogFileGetEndTime(handle, ct.byref(time))
        return datetime.datetime.fromtimestamp(time.value)

    @property
    @_mounted_handle
    def start_time(self, handle):
        """`datetime.datetime`: The time of the first event in the log file"""
        time = ct.c_uint32()
        dll.kvmLogFileGetStartTime(handle, ct.byref(time))
        return datetime.datetime.fromtimestamp(time.value)

    @property
    @_mounted_handle
    def log_type(self, handle):
        """`~canlib.kvmlib.enums.LogFileType`: The type of the log file

        .. versionadded:: 1.11

        """
        type_ = ct.c_int32()
        dll.kvmLogFileGetType(handle, self.index, ct.byref(type_))
        return LogFileType(type_.value)

    def event_count_estimation(self):
        """Returns an approximation of the number of events

        The number is a rough estimation because it is calculated from the
        number of blocks allocated by the log file on the disk as an
        optimization.

        .. versionadded:: 1.7

        """
        # The only way to get the event count approximation from the underlying
        # dll is during mounting (in kvmLogFileMountEx())
        return self._remount()

    def _remount(self):
        return self._container._mount(self.index)
