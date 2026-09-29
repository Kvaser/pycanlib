import ctypes as ct

from .. import deprecation
from .enums import FileFormat
from .properties import _PROPERTY_TYPE
from .wrapper import dll


def writer_formats():
    """Return a generator of all writer formats.

    You may list available Writers using::

        >>> from canlib import kvlclib
        >>> for format in kvlclib.writer_formats():
        ...     print(format)
        CSV (.csv): Writer, CAN frames in CSV format
        CSV_SIGNAL (.csv): Writer, Selected signals in CSV format
        XCP (.csv): Writer, CCP/XCP calibration in CSV format
        MATLAB (.mat): Writer, Selected signals in Matlab format for ATI Vision
        KME24 (.kme): Writer, Kvaser binary format (KME 2.4) - used for Vector CANalyzer
        KME25 (.kme25): Writer, Kvaser binary format (KME 2.5)
        KME40 (.kme40): Writer, Kvaser binary format (KME 4.0)
        KME50 (.kme50): Writer, Kvaser binary format (KME 5.0)
        PLAIN_ASC (.txt): Writer, CAN frames in plain text format
           ...

    .. versionadded:: 1.7

    """
    id_ = ct.c_int()
    dll.kvlcGetFirstWriterFormat(ct.byref(id_))
    while id_.value != FileFormat.INVALID:
        yield WriterFormat(FileFormat(id_.value))
        previous_id = id_.value
        dll.kvlcGetNextWriterFormat(previous_id, ct.byref(id_))


class WriterFormat:
    """Helper class that encapsulates a Writer.

    You may use `writer_formats()` to list available Writers.

    .. versionchanged:: 1.19
       Updated formating in `__str__`.

    """

    @classmethod
    @deprecation.deprecated.favour("kvlclib.writer_formats")
    def getFirstWriterFormat(cls):
        """Get the first supported output format."""
        id_ = ct.c_int()
        dll.kvlcGetFirstWriterFormat(ct.byref(id_))
        return FileFormat(id_.value)

    @classmethod
    @deprecation.deprecated.favour("kvlclib.writer_formats")
    def getNextWriterFormat(cls, previous_id):
        """Get the next supported output format."""
        id_ = ct.c_int()
        dll.kvlcGetNextWriterFormat(previous_id, ct.byref(id_))
        return FileFormat(id_.value)

    def __init__(self, id_):
        self.id_ = id_
        self.name = "Unknown name"
        self.extension = "Unknown extension"
        self.description = "Unknown description"

        text = ct.create_string_buffer(256)
        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetWriterName(self.id_, text, text_len)
        self.name = text.value.decode('utf-8')

        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetWriterExtension(self.id_, text, text_len)
        self.extension = text.value.decode('utf-8')

        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetWriterDescription(self.id_, text, text_len)
        self.description = text.value.decode('utf-8')

    def __repr__(self):
        text = f"WriterFormat({self.id_!r})"
        return text

    def __str__(self):
        text = f"{self.id_.name} (.{self.extension}): Writer, {self.description}"
        return text

    def isPropertySupported(self, wr_property):
        """Check if specified write property is supported.

        Retuns True if the property is supported by output format.

        Args:
            wr_property (`Property`): Writer property

        Returns:
            `bool`
        """
        supported = ct.c_int()
        # Backward compatibility with deprecated kvlclib.PROPERTY_XXX
        if isinstance(wr_property, dict):
            wr_property = wr_property['value']
        dll.kvlcIsPropertySupported(self.id_, wr_property, ct.byref(supported))
        return bool(supported.value)

    def getPropertyDefault(self, wr_property):
        """Get default value for property."""
        if wr_property is None:
            buf = ct.c_bool()
        else:
            # Backward compatibility with deprecated kvlclib.PROPERTY_XXX
            if isinstance(wr_property, dict):
                buf = wr_property['type']
                wr_property = wr_property['value']
            else:
                if _PROPERTY_TYPE[wr_property] is None:
                    return None
                buf = _PROPERTY_TYPE[wr_property]()
        dll.kvlcGetWriterPropertyDefault(self.id_, wr_property, ct.byref(buf), ct.sizeof(buf))
        return buf.value
