"""Wrapper for the Kvaser kvaDbLib library

A CAN database contains information about messages. Each message has (among
other attributes) an identifier, a name and one or several signals. The
kvaDbLib library is an API for these CAN databases.

"""

from .attribute import Attribute
from .attributedef import (AttributeDefinition, DefaultDefinition,
                           EnumDefaultDefinition, EnumDefinition,
                           FloatDefinition, IntegerDefinition,
                           HexDefinition,
                           MinMaxDefinition, StringDefinition)
from .bound_message import BoundMessage
from .bound_signal import BoundSignal
from .constants import *
from .dbc import DATABASE_FLAG_J1939, Dbc
from .enums import (AttributeOwner, AttributeType, Error, MessageFlag,
                    ProtocolType, SignalByteOrder, SignalMultiplexMode,
                    SignalType)
from .exceptions import (KvdBufferTooSmall, KvdDbFileParse, KvdErrInParameter,
                         KvdError, KvdInUse, KvdNoAttribute, KvdNoMessage,
                         KvdNoNode, KvdNoSignal, KvdNotFound, KvdOnlyOneAllowed,
                         KvdWrongOwner)
from .framebox import FrameBox, SignalNotFound
from .message import Message
from .node import Node
from .signal import EnumSignal, Signal, ValueLimits, ValueScaling, ValueSize
from .wrapper import (bytes_to_dlc, dlc_to_bytes, dllversion,
                      get_last_parse_error, get_protocol_properties)
