import ctypes as ct

from .enums import FileFormat
from .exceptions import KvlcNotImplemented
from .properties import _PROPERTY_TYPE
from .wrapper import dll


def reader_formats():
    """Return a generator of all reader formats.

    .. versionadded:: 1.7

    """
    id_ = ct.c_int()
    dll.kvlcGetFirstReaderFormat(ct.byref(id_))
    while id_.value != FileFormat.INVALID:
        yield ReaderFormat(FileFormat(id_.value))
        previous_id = id_.value
        dll.kvlcGetNextReaderFormat(previous_id, ct.byref(id_))


class ReaderFormat(object):
    """Helper class that encapsulates a Reader.

    You may list available Readers using::

        for format in kvlclib.reader_formats():
            print(format)

    .. versionadded:: 1.7

    """

    def __init__(self, id_):
        self.id_ = id_
        self.name = "Unknown name"
        self.extension = "Unknown extension"
        self.description = "Unknown description"

        text = ct.create_string_buffer(256)
        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetReaderName(self.id_, text, text_len)
        self.name = text.value.decode('utf-8')

        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetReaderExtension(self.id_, text, text_len)
        self.extension = text.value.decode('utf-8')

        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetReaderDescription(self.id_, text, text_len)
        self.description = text.value.decode('utf-8')

    def __repr__(self):
        text = "ReaderFormat({!r})".format(self.id_)
        return text

    def __str__(self):
        text = "%4d: %s (.%s)" % (self.id_, self.name, self.extension)
        text += " Reader"
        text += ", %s" % self.description
        return text

    def isPropertySupported(self, rd_property):
        """Check if specified read property is supported.

        Retuns True if the property is supported by input format.

        Args:
            rd_property (`canlib.kvlclib.Property`): Reader property
        """
        supported = ct.c_int()

        # Not all readers has implemented kvlcIsPropertySupported()
        # Especially #6
        try:
            dll.kvlcIsPropertySupported(self.id_, rd_property, ct.byref(supported))
        except KvlcNotImplemented:
            return False
        return bool(supported.value)

    def getPropertyDefault(self, rd_property):
        """Get default value for property."""
        if rd_property is None:
            buf = ct.c_bool()
        else:
            buf = _PROPERTY_TYPE[rd_property]()
        dll.kvlcGetReaderPropertyDefault(self.id_, rd_property, ct.byref(buf), ct.sizeof(buf))
        return buf.value
