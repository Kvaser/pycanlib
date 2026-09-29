"""Wrapper module for the Kvaser converter library kvlclib.

This module wraps the Kvaser kvlclib dll. For more info, see the kvlclib help
files which are availible in the CANlib SDK.
https://www.kvaser.com/developer/canlib-sdk/

"""

from .constants import *
from .converter import Converter
from .deprecated import KvlcLib as Kvlclib  # for backwards-compatibility
from .deprecated import *
from .enums import ChannelMask, Error, FileFormat
from .exceptions import (KvlcEndOfFile, KvlcError, KvlcFileExists,
                         KvlcNotImplemented)
from .properties import Property
from .readerformat import ReaderFormat, reader_formats
from .wrapper import dllversion, getVersion
from .writerformat import WriterFormat, writer_formats
