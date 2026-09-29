import ctypes as ct
import os

from .. import deprecation
from ..futureapi import NotYetSupportedError
from .enums import FileType
from .events import memoLogEventEx
from .exceptions import KvmNoLogMsg, kvm_error
from .wrapper import dll


# It would be nice if we set filetype based on path extension,
# but since only KME50 is fully supported, we don't do that yet.
def createKme(path, filetype=FileType.KME50):
    """Create a KME file on the host computer

    Arguments:

        path (`str`): The full filepath for the .KME file
            (e.g. ``"data/mylog.kme50"``).

        filetype (`FileType`): The KME file type

    Returns:
        `Kme`

    .. versionadded:: 1.7

    """
    status_p = ct.c_int32()
    ct_filename = ct.c_char_p(path.encode('utf-8'))
    kme_handle = dll.kvmKmeCreateFile(ct_filename, ct.byref(status_p), filetype)
    if filetype == FileType.KME50:
        return Kme50(kme_handle)
    elif filetype == FileType.KME60:
        return Kme60(kme_handle)
    else:
        return Kme(kme_handle)


def openKme(path, filetype=FileType.KME50):
    """Open a KME file on the host computer

    Arguments:

        path (`str`): The full filepath for the .KME file
            (e.g. ``"data/mylog.kme50"``).

        filetype (`FileType`): The KME file type

    Returns:
        `Kme`

    .. versionadded:: 1.7

    """
    status_p = ct.c_int32()
    kme_handle = dll.kvmKmeOpenFile(path.encode('utf-8'), ct.byref(status_p), filetype)
    if status_p.value != 0:
        print(f"ERROR openKme failed with filename:{path}, filetype:{filetype}\n")
        raise kvm_error(status_p.value)

    if filetype == FileType.KME50:
        return Kme50(kme_handle)
    elif filetype == FileType.KME60:
        return Kme60(kme_handle)
    else:
        return Kme(kme_handle)


def kme_file_type(path):
    """Scan KME file and report version

    Open and read the file `path` and try to decode what version
    of KME it contains.

    Arguments:

        path (`str`): The full filepath for the .KME file
            (e.g. ``"data/mylog.kme"``).

    Returns:
        `FileType`: The KME file type

    .. versionadded:: 1.7

    """
    type = ct.c_int32()
    filename = os.path.realpath(path)
    ct_filename = ct.c_char_p(filename.encode('utf-8'))
    dll.kvmKmeScanFileType(ct_filename, ct.byref(type))
    return FileType(type.value)


def _dump_hex(text, data, group_size=4):
    hexstring = ''.join([f'{b:02x}' for b in data])
    n = group_size
    grouped_hexstring = [hexstring[i:i + n] for i in range(0, len(hexstring), n)]
    print(text, ' '.join(grouped_hexstring))


class Kme:
    """A kme file

    A class representing a KME file. The main use is twofold:

    Either we create a KME file using `createKme` and would like to write
    events using `Kme.write_event`::

        with kvmlib.createKme('out/data.kme50') as kme:
            ...
            kme.write_event(my_logevent)

    Or we read events from an existing KME file::

        with kvmlib.openKme('in/data.kme50') as kme:
            event = kme.read_event()
            ...
            print(event)

    Note that only KME files of type KME50 and KME60 may currently be written to.

    .. versionadded:: 1.7

    .. versionchanged:: 1.20
        Added experimental support for KME60.

    """

    def __init__(self, handle):
        self.handle = handle

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def __iter__(self):
        return self.events()

    def event_count_estimation(self):
        """Returns an approximation of the number of events contained in the KME file.

            Returns:
                `int`: Approximate number of events in KME file.

        .. versionadded:: 1.11

        """
        try:
            eventCount = ct.c_int64(0)
            dll.kvmKmeCountEventsEx(self.handle, ct.byref(eventCount))
        except NotYetSupportedError:
            eventCount = ct.c_uint32(0)
            dll.kvmKmeCountEvents(self.handle, ct.byref(eventCount))
        return eventCount.value

    @deprecation.deprecated.replacedby(event_count_estimation)
    def estimate_events(self):
        """Estimate how many events the KME file contains

            Returns:
                `int`: Approximate number of events in KME file.

        .. versionadded:: 1.7
        .. deprecated:: 1.11

        """
        eventCount = ct.c_uint32(0)
        dll.kvmKmeCountEvents(self.handle, ct.byref(eventCount))
        return eventCount.value

    def events(self):
        while True:
            try:
                event = self.read_event()
            except (KvmNoLogMsg):
                return
            yield event

    def read_event(self):
        """Read logevent from KME file

            Returns:
                `memoLogEventEx`

        .. versionadded:: 1.7

        """
        logevent = memoLogEventEx()
        dll.kvmKmeReadEvent(self.handle, logevent)
        # _dump_hex("Reading event:", logevent.event.raw.data)
        return logevent

    # Read + write does not produce identical files for formats other than KME50...
    def write_event(self, logevent):
        raise NotImplementedError("Writing is only supported for filetype KME50")

    def close(self):
        if self.handle is not None:
            dll.kvmKmeCloseFile(self.handle)
            self.handle = None


class Kme50(Kme):
    def read_event(self):
        """Read logevent from KME50 file

            Returns:
                `kvmlib.events.LogEvent`: E.g. `kvmlib.events.MessageEvent`.

        .. versionadded:: 1.7

        """
        logevent = super().read_event()
        return logevent.createMemoEvent()

    def write_event(self, event):
        """Write logevent to KME50 file

            Arguments:

                logevent (`kvmlib.events.LogEvent`): The event to write,
                    (e.g. `kvmlib.events.MessageEvent`).

        .. versionadded:: 1.7

        """
        mrt = event._asMrtEvent()
        mle = memoLogEventEx(mrt)
        # _dump_hex("writing event:", mle.event.raw.data)
        dll.kvmKmeWriteEvent(self.handle, ct.byref(mle))


class Kme60(Kme50):
    """Experimental support for Kme60 currently only includes identical events to Kme50.

        .. versionadded:: 1.20

    """
    pass
