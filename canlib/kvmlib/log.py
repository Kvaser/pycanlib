import ctypes as ct

from ..futureapi import NotYetSupportedError
from .exceptions import LockedLogError
from .logfile import LogFile
from .wrapper import dll


class UnmountedLog(object):
    """The log area of a Memorator before mounting

    Before the log area of a `canlib.kvmlib.Memorator` object has been mounted,
    its `log` attribute is set to an instance of this class.

    This class has all the functionality available even when the log area has
    not been mounted -- this functionality is still present after the log area
    has been mounted (or if the area is always mounted -- see
    `canlib.kvmlib.Kmf`).

    The number of log files can be read as the ``len()`` of this object
    (``container`` is either a `canlib.kvmlib.Memorator` or `canlib.kvmlib.Kmf`
    object)::

        num_log_files = len(container.log)

    All log files can also be deleted::

        container.log.delete_all()

    .. versionadded:: 1.6

    """

    def __init__(self, memorator):
        # We assume this object will not out-live the memorator object
        self.handle = memorator.handle

    def __len__(self):
        count = ct.c_uint32()
        dll.kvmLogFileGetCount(self.handle, ct.byref(count))
        return count.value

    def delete_all(self):
        """Delete all log files"""
        dll.kvmLogFileDeleteAll(self.handle)


class MountedLog(UnmountedLog):
    """The log area of a Memorator once mounted

    Once a `canlib.kvmlib.Memorator` object has been mounted, its `log`
    attribute is set to an instance of this class. This is the preferred way of
    using this class.

    For `canlib.kvmlib.Kmf` objects, the `log` attribute is always an instance
    of this class as they are by definition mounted.

    In the following examples ``container`` can be either a
    `canlib.kvmlib.Memorator` object that has been mounted, or a
    `canlib.kvmlib.Kmf` object.

    The files within the log can be accessed via indexing::

        container.log[index]

    or all files can be iterated over::

        for log_file in container.log:
            ...

    The log area can also be validated::

            container.log.validate()

    Also see the super class `canlib.kvmlib.UnmountedLog` for functionality
    this class has inherited.

    .. versionadded:: 1.6

    """

    _mounted_index = None  #: The index of the currently mounted log file

    #: When True, attempts to mount log files will raise LockedLogError
    _mount_lock = False

    def __init__(self, memorator, ldf_version):
        # We assume this object will not out-live the memorator object
        super(MountedLog, self).__init__(memorator)
        self.ldf_version = ldf_version

    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError("Index out of range")
        else:
            return LogFile(self, index)

    def validate(self):
        """Raises the corresponding exception if any errors are detected"""
        dll.kvmKmfValidate(self.handle)

    def _mount(self, index):
        if self._mount_lock:
            raise LockedLogError()
        # Its ok to dismount even if we aren't mounted
        dll.kvmLogFileDismount(self.handle)

        try:
            event_count = ct.c_int64()
            dll.kvmLogFileMountEx(self.handle, index, ct.byref(event_count))
        except NotYetSupportedError:
            event_count = ct.c_uint32()
            dll.kvmLogFileMount(self.handle, index, ct.byref(event_count))
        self._mounted_index = index

        return event_count.value
