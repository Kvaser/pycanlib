import ctypes as ct

from .enums import FileFormat
from .exceptions import KvlcNotImplemented
from .properties import _PROPERTY_TYPE
from .wrapper import dll


def reader_formats():
    """Return a generator of all reader formats.

    You may list available Readers using::

        >>> from canlib import kvlclib
        >>> for format in kvlclib.reader_formats():
        ...     print(format)
        KME24 (.kme): Reader, Kvaser binary format (KME 2.4)
        KME25 (.kme25): Reader, Kvaser binary format (KME 2.5)
        KME40 (.kme40): Reader, Kvaser binary format (KME 4.0)
        KME50 (.kme50): Reader, Kvaser binary format (KME 5.0)
        MDF (.log): Reader, CAN frames in Vector Mdf
        MDF_4X (.mf4): Reader, CAN frames in MDF v4.1 for Vector CANalyzer
        PLAIN_ASC (.txt): Reader, CAN frames in plain text format
        VECTOR_ASC (.asc): Reader, CAN frames in Vector ASCII format
        VECTOR_BLF_FD (.blf): Reader, CAN frames in Vector BLF format
        CSV (.csv): Reader, CAN frames in CSV format
           ...

    NOTE:

        CANlib before v5.37 incorrectly reported ``.mke`` as the file suffix for KME 2.4.

    .. versionadded:: 1.7

    """
    id_ = ct.c_int()
    dll.kvlcGetFirstReaderFormat(ct.byref(id_))
    while id_.value != FileFormat.INVALID:
        yield ReaderFormat(FileFormat(id_.value))
        previous_id = id_.value
        dll.kvlcGetNextReaderFormat(previous_id, ct.byref(id_))


class ReaderFormat:
    """Helper class that encapsulates a Reader.

    You may use `reader_formats()` to list available Readers.

    .. versionadded:: 1.7

    .. versionchanged:: 1.19
       Updated formating in `__str__`.

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
        text = f"ReaderFormat({self.id_!r})"
        return text

    def __str__(self):
        text = f"{self.id_.name} (.{self.extension}): Reader, {self.description}"
        return text

    def isPropertySupported(self, rd_property):
        """Check if specified read property is supported.

        Retuns True if the property is supported by input format.

        Args:
            rd_property (`Property`): Reader property
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
            if _PROPERTY_TYPE[rd_property] is None:
                return None
            buf = _PROPERTY_TYPE[rd_property]()
        dll.kvlcGetReaderPropertyDefault(self.id_, rd_property, ct.byref(buf), ct.sizeof(buf))
        return buf.value
