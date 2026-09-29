""" Support for accessing information within compiled t program (.txe) files. """

import ctypes as ct
from collections import namedtuple
from datetime import datetime

from canlib.canlib import TxeDataItem, TxeFileIsEncrypted

from ..versionnumber import VersionNumber
from .wrapper import dll

SourceElement = namedtuple('SourceElement', 'name contents')


class Txe:
    """The Txe class provides an interface to compiled t programs (.txe) files.

    .. versionadded:: 1.6

    """

    def __init__(self, path):
        """Create a Txe object for the file found at path.

        Args:
            path (str): Path of the compiled t (.txe) file.
        """
        self._c_path = ct.c_char_p(path.encode('utf-8'))

    def _size_of_item_data(self, item):
        """ If buffer argument is None, then kvScriptTxeGetData stores the required buffer size in buffer_size. """
        buffer_size = ct.c_uint(0)
        dll.kvScriptTxeGetData(
            self._c_path, item, None, buffer_size
        )  # pylint: disable=maybe-no-member
        return buffer_size.value

    def _read_item(self, item, expected_buffer_type):
        data = expected_buffer_type()
        # ctypes refuses to cast python int to LP_c_ulong
        buffer_size = ct.c_uint(ct.sizeof(data))
        dll.kvScriptTxeGetData(
            self._c_path, item, data, buffer_size
        )  # pylint: disable=maybe-no-member
        assert buffer_size.value == ct.sizeof(data)
        return data

    def _read_variable_size_item(self, item):
        size = self._size_of_item_data(item)
        if size != 0:
            # Return raw to preserve any potentially embedded '\x00' within data.
            # For example TxeDataItem.SOURCE returns data containing multiple strings separated by '\x00'.
            item = self._read_item(item, ct.c_char * size).raw
        else:
            item = b''
        return item

    @property
    def path(self):
        """str: Path of compiled t program (.txe) file. """
        return self._c_path.value.decode('utf-8')

    @property
    def file_version(self):
        """`~canlib.versionnumber.VersionNumber`: .txe binary format version number."""
        values = self._read_item(TxeDataItem.FILE_VERSION, ct.c_uint32 * 3)
        return VersionNumber(*values)

    @property
    def compiler_version(self):
        """`~canlib.versionnumber.VersionNumber`: t compiler version number."""
        values = self._read_item(TxeDataItem.COMPILER_VERSION, ct.c_uint32 * 3)
        return VersionNumber(*values)

    @property
    def date(self):
        """`datetime.datetime`: Compilation date and time."""
        values = self._read_item(TxeDataItem.DATE, ct.c_uint32 * 6)
        return datetime(*values)

    @property
    def description(self):
        """str: t program description."""

        return (
            self._read_variable_size_item(TxeDataItem.DESCRIPTION).rstrip(b'\x00').decode('utf-8')
        )

    @property
    def source(self):
        """Yields name and content of the source files used to create the .txe binary file.

        If the t source files used to create the .txe binary was included at
        compilation time, then this attribute will yield `SourceElement` tuples
        containing the name and content of the individual source files.

        Sample usage::

          for name, contents in txe.source:
            print('file name:{} contents:{}'.format(name, contents))

        If the source and byte-code sections of the .txe binary have been encrypted then it's
        not possible to parse the source list and a `TxeFileIsEncrypted` exception will
        be raised.

        If no source files have been included in the .txe binary then an empty iterator
        is returned.

        Yields:
            `SourceElement`: Name and contents tuple.

        Raises:
            TxeFileIsEncrypted: If the source and byte-code sections of the .txe binary have been encrypted.
        """
        if self.is_encrypted:
            raise TxeFileIsEncrypted('It is not possible to decode an encrypted source code list')

        source_list = self._read_variable_size_item(TxeDataItem.SOURCE).rstrip(b'\x00')
        iterator = (entry.decode('utf-8') for entry in source_list.split(b'\x00'))
        return (SourceElement(name, contents) for name, contents in zip(iterator, iterator))

    @property
    def is_encrypted(self):
        """bool: true if the source and byte-code sections of the .txe binary have been encrypted."""
        values = self._read_item(TxeDataItem.IS_ENCRYPTED, ct.c_uint32 * 1)
        return values[0] != 0

    @property
    def size_of_code(self):
        """int: Size in bytes of byte-code section."""
        values = self._read_item(TxeDataItem.SIZE_OF_CODE, ct.c_uint32 * 1)
        return values[0]
