import ctypes as ct
import os

from .. import deprecation
from ..futureapi import NotYetSupportedError
from .properties import _PROPERTY_TYPE
from .readerformat import ReaderFormat
from .writerformat import WriterFormat
from .wrapper import dll


class Converter:
    """A kvlclib converter

    This class wraps all kvlclib functions related to converters, and saves you
    from keeping track of a handle and passing that to the functions.

    `kvlcCreateConverter` and `kvlcDeleteConverter` are not wrapped as they are
    called when Converter objects are created and deleted,
    respectively. However, if it is necessary to force the converter to write
    its files, `flush` can be used to simulate destroying and recreating the
    converter object.

    Args:
        filename (`str`): Name of output file
        file_format (`.FileFormat` | `.WriterFormat` ): A supported output format

    Note:
        No more than 128 converters can be open at the same time.

    .. versionchanged:: 1.18
        The `file_format` parameter now accepts `.WriterFormat` as well.

    """

    def __init__(self, filename, file_format):
        self.format = file_format
        self.handle = ct.c_void_p(None)
        self.filename = os.path.realpath(filename)
        if isinstance(file_format, WriterFormat):
            file_format = file_format.id_
        self.file_format = file_format
        dll.kvlcCreateConverter(ct.byref(self.handle), self.filename.encode(), self.file_format)

    def __del__(self):
        """Delete the converter and close all files."""
        dll.kvlcDeleteConverter(self.handle)

    def addDatabaseFile(self, filename, channel_mask):
        """Add a database file.

        Converters with the property `Property.SIGNAL_BASED` will match
        events against all entries in the database and write signals to the
        output file.

        Args:
            filename (`str`): Path to database file (.dbc)
            channel_mask (`ChannelMask`): Channels to use database on

        """
        filename = os.path.realpath(filename)
        ct_filename = ct.c_char_p(filename.encode('utf-8'))
        dll.kvlcAddDatabaseFile(self.handle, ct_filename, channel_mask)

    def attachFile(self, filename):
        """Attach file to be included in the output file.

        E.g. used to add a database or a movie to the output.

        Note that the output format must support the property
        `.Property.ATTACHMENTS`.

        Args:
            filename (`str`): Path to file to be attached

        """
        filename = os.path.realpath(filename)
        ct_filename = ct.c_char_p(filename.encode('utf-8'))
        dll.kvlcAttachFile(self.handle, ct_filename)

    def convertEvent(self):
        """Convert next event.

        Convert one event from input file and write it to output file.
        """
        dll.kvlcConvertEvent(self.handle)

    def feedLogEvent(self, event):
        """Feed one event to the converter.

        Used when reading log files directly from device.

        """
        # event should be of type memoLogEventEx
        # event._asMrtEvent()
        memoLogEventEx = event._asMrtEvent()
        dll.kvlcFeedLogEvent(self.handle, ct.byref(memoLogEventEx))

    def feedNextFile(self):
        """Prepare for new file

        Notify the converter that next event in `feedLogEvent()` will come
        from another file. Used when reading log files directly from device.

        E.g. use this function with `FileFormat.MEMO_LOG` when using
        KVMLIB to read events from a Kvaser Memorator connected to USB.

        .. versionadded:: 1.18

        """

    def flush(self):
        """Recreate the converter so changes are saved to disk

        Converters do not write changes to disk until they are deleted. This
        method deletes and recreates the underlying C converter, without
        needing to recreate the Python object.

        """
        self.__del__()
        self.__init__(self.filename, self.file_format)

    def getDlcMismatch(self):
        """Return a dictionary with id, DLC with number of mismatched messages

        If any DLC mismatch occurred during conversion (which can be seen using
        `isDlcMismatch`) this function returns a dictonary with the tuple
        message id and message DLC as key, and the number of times that
        triggered the mismatch as value.

        """
        max_length = ct.c_uint(0)
        dll.kvlcGetDlcMismatchList(self.handle, None, None, None, ct.byref(max_length))
        msg_id = (ct.c_uint * max_length.value)()
        msg_dlc = (ct.c_uint * max_length.value)()
        msg_occurance = (ct.c_uint * max_length.value)()
        dll.kvlcGetDlcMismatchList(
            self.handle, msg_id, msg_dlc, msg_occurance, ct.byref(max_length)
        )
        mismatch_counter = {}
        for i in range(max_length.value):
            mismatch_counter[(msg_id[i], msg_dlc[i])] = msg_occurance[i]
        return mismatch_counter

    def getProperty(self, wr_property):
        """Get current value for a writer property.

        Args:
            wr_property (`.Property`): Writer property to get
        """
        # Backward compatibility with deprecated kvlclib.PROPERTY_XXX
        if isinstance(wr_property, dict):
            buf = wr_property['type']
            wr_property = wr_property['value']
        else:
            buf = _PROPERTY_TYPE[wr_property]()
        dll.kvlcGetProperty(self.handle, wr_property, ct.byref(buf), ct.sizeof(buf))
        return buf.value

    def getOutputFilename(self):
        """Get the filename of the current output file."""
        filename = ct.create_string_buffer(256)
        dll.kvlcGetOutputFilename(self.handle, filename, ct.sizeof(filename))
        return filename.value.decode('utf-8')

    def nextInputFile(self, filename):
        """Select next input file."""
        filename = os.path.realpath(filename)
        ct_filename = ct.c_char_p(filename.encode('utf-8'))
        dll.kvlcNextInputFile(self.handle, ct_filename)

    def eventCount(self):
        """Get extimated number of events left.

        Get the estimated number of remaining events in the input file. This
        can be useful for displaying progress during conversion.
        """
        try:
            count = ct.c_int64(0)
            dll.kvlcEventCountEx(self.handle, ct.byref(count))
        except NotYetSupportedError:
            count = ct.c_uint(0)
            dll.kvlcEventCount(self.handle, ct.byref(count))
        return count.value

    def setProperty(self, wr_property, value):
        """Set a property value.

        Args:
            wr_property (`.Property`): Writer property to be set
        """
        # Backward compatibility with deprecated kvlclib.PROPERTY_XXX
        if isinstance(wr_property, dict):
            buf = wr_property['type']
            wr_property = wr_property['value']
        else:
            buf = _PROPERTY_TYPE[wr_property]()
        buf.value = value
        dll.kvlcSetProperty(self.handle, wr_property, ct.byref(buf), ct.sizeof(buf))

    def isDlcMismatch(self):
        """Get DLC mismatch status.

        DLC mismatch occurs when a CAN id is found in the database but the DLC
        differs from the DLC in the message.

        """
        mismatch = ct.c_int()
        dll.kvlcIsDlcMismatch(self.handle, ct.byref(mismatch))
        return mismatch.value

    def resetDlcMismatch(self):
        """Reset DLC mismatch status."""
        dll.kvlcResetDlcMismatch(self.handle)

    def isOutputFilenameNew(self):
        """Check if the converter has created a new file.

        This is only true once after a a new file has been created. Used when
        splitting output into multiple files.
        """
        updated = ct.c_int()
        dll.kvlcIsOutputFilenameNew(self.handle, ct.byref(updated))
        return updated.value

    @deprecation.deprecated.replacedby(isOutputFilenameNew)
    def IsOutputFilenameNew(self):
        """Check if the converter has created a new file.

        .. deprecated:: 1.5
            Use `isOutputFilenameNew` instead.

        """
        pass

    def isOverrunActive(self):
        """Get overrun status.

        Overruns can occur during logging with a Memorator if the bus load
        exceeds the logging capacity. This is very unusual, but can occur if a
        Memorator runs complex scripts and triggers.
        """
        overrun = ct.c_int()
        dll.kvlcIsOverrunActive(self.handle, ct.byref(overrun))
        return overrun.value

    @deprecation.deprecated.replacedby(isOverrunActive)
    def IsOverrunActive(self):
        """Get overrun status.

        .. deprecated:: 1.5
            Use `isOverrunActive` instead.

        """
        pass

    def resetOverrunActive(self):
        """Reset overrun status."""
        dll.kvlcResetOverrunActive(self.handle)

    def isDataTruncated(self):
        """Get truncation status.

        Truncation occurs when the selected output converter can't write all
        bytes in a data frame to file. This can happen if CAN FD data is
        extracted to a format that only supports up to 8 data bytes,
        e.g. `.FileFormat.KME40`.

        Truncation can also happen if `.Property.LIMIT_DATA_BYTES` is
        set to limit the number of data bytes in output.

        Returns:
            True if data has been truncated

        """
        truncated = ct.c_int()
        dll.kvlcIsDataTruncated(self.handle, ct.byref(truncated))
        return truncated.value

    @deprecation.deprecated.replacedby(isDataTruncated)
    def IsDataTruncated(self):
        """Get truncation status.

        .. deprecated:: 1.5
            Use `.isDataTruncated` instead.

        """
        pass

    def resetStatusTruncated(self):
        """Reset data trunctation status."""
        dll.kvlcResetDataTruncated(self.handle)

    def setInputFile(self, filename, file_format):
        """Select input file.

        Args:
            filename (string): Name of input file
            file_format (`.FileFormat` | `.ReaderFormat` ): A supported input format

        .. versionchanged:: 1.16
            The `file_format` parameter now accepts `.ReaderFormat` as well.

        .. versionchanged:: 1.18
            If `filename` is `None`, the format for `feedLogEvent` is set.

        """
        if isinstance(file_format, ReaderFormat):
            file_format = file_format.id_
        if filename is None:
            dll.kvlcFeedSelectFormat(self.handle, file_format)
        else:
            filename = os.path.realpath(filename)
            ct_filename = ct.c_char_p(filename.encode('utf-8'))
            dll.kvlcSetInputFile(self.handle, ct_filename, file_format)

    @deprecation.deprecated.favour(".format.getPropertyDefault")
    def getPropertyDefault(self, wr_property):
        """Get default property.

        .. deprecated:: 1.5
            Use `.WriterFormat.getPropertyDefault` instead.

        """
        return self.format.getPropertyDefault(wr_property)

    @deprecation.deprecated.favour(".format.isPropertySupported")
    def isPropertySupported(self, wr_property):
        """Check if specified wr_property is supported by the current format.

        .. deprecated:: 1.5
            Use `.WriterFormat.isPropertySupported` instead.

        """
        return self.format.isPropertySupported(wr_property)
