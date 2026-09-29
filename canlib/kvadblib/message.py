"""Wrapper for Kvaser Database API (kvaDbLib)."""

import ctypes as ct

from ..canlib import MessageFlag as CanMessageFlag
from ..frame import Frame
from . import wrapper
from .attribute import Attribute
from .bound_message import BoundMessage
from .enums import (AttributeOwner, MessageFlag, SignalByteOrder,
                    SignalMultiplexMode, SignalType)
from .exceptions import (KvdNoAttribute, KvdNoMessage, KvdNoSignal,
                         KvdWrongOwner)
from .node import Node
from .signal import EnumSignal, Signal
from .wrapper import dll


def _signal_object(db, msg, handle):
    """Instantiate either a `Signal` or an `EnumSignal`

    This function checks whether the signal pointed to by ``handle`` has any
    enumeration values; if it does, an `EnumSignal` is created and
    returned -- otherwise, a `Signal` is created and returned.

    """
    try:
        dll.kvaDbGetFirstEnumValue(handle, ct.c_void_p())
    except KvdNoAttribute:
        return Signal(db, msg, handle, mode=None, scaling=None)
    else:
        return EnumSignal(db, msg, handle, mode=None, scaling=None)


class Message:
    """Database message, holds signals."""

    def __init__(self, db, handle, name=None, id=None, flags=None, dlc=None, comment=None):
        """Create a message and optionally set name, id and/or flags."""
        self._handle = handle
        self._can_data = ct.create_string_buffer(64)  # for signal data
        # We need to save a pointer to the database since the API does not have
        # a way to get database handle from a message handle
        self._db = db
        if name is not None:
            self.name = name
        if id is not None:
            self.id = id
        if flags is not None:
            self.flags = flags
        if dlc is not None:
            self.dlc = dlc
        if comment is not None:
            self.comment = comment

    def __eq__(self, other):
        attrs = 'comment dlc id flags name'.split()
        return all(getattr(self, a) == getattr(other, a) for a in attrs)

    def __iter__(self):
        return self.signals()

    def __len__(self):
        """Returns number of signals in message."""
        return sum(1 for _ in self)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        # __repr__ should never do any calls to the dll, so this needs to be done in __str__
        return "Message(name={!r}, id={!r}, flags={!r}, dlc={!r}, comment={!r})".format(
            self.name, self.id, self.flags, self.dlc, self.comment
        )

    def asframe(self):
        """Returns a `~canlib.Frame` object with flags and empty data matching this message

        .. versionchanged:: 1.21 Now includes support for CAN FD signals in dbc
            file introduced in CANlib SDK v5.39 by using the `.canflags`
            properties.

        """
        can_flags = self.canflags
        if CanMessageFlag.FDF not in can_flags:
            length = wrapper.dlc_to_bytes(
                self.dlc,
                self._db.protocol.value,
            )
        else:
            length = self.dlc
        return Frame(id_=self.id, data=bytearray(length), flags=can_flags)

    def attributes(self):
        """Return a generator over all message attributes."""
        ah = None
        nah = ct.c_void_p()
        try:
            dll.kvaDbGetFirstMsgAttribute(self._handle, ct.byref(nah))
        except KvdNoAttribute:
            return
        while nah.value is not None:
            ah, nah = nah, ct.c_void_p()
            yield Attribute(self, ah)
            try:
                dll.kvaDbGetNextAttribute(ah, ct.byref(nah))
            except KvdNoAttribute:
                return

    def bind(self, frame=None):
        """Bind this message to a frame

        Creates a new BoundMessage object representing this message bound to
        the given Frame object, or a new Frame object if `frame` is `None`.

        """
        return BoundMessage(self, frame or self.asframe())

    def delete_attribute(self, name):
        """Delete attribute from message."""
        ah = ct.c_void_p()
        dll.kvaDbGetMsgAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        dll.kvaDbDeleteMsgAttribute(self._handle, ah)

    def delete_signal(self, signal):
        """Delete signal from message.

        Args:
            signal (`Signal`): signal to be deleted

        """
        dll.kvaDbDeleteSignal(self._handle, signal._handle)

    def get_attribute_value(self, name):
        """Return attribute value

        If the attribute is not set on the message, we return the attribute
        definition default value.

        .. versionchanged:: 1.18
            When an EnumAttribute is not set, the default value will now be
            returned as `int` (instead of `EnumValue` with empty `name`).

        """
        ah = ct.c_void_p()

        # Try and find attribute on message
        try:
            dll.kvaDbGetMsgAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        except KvdNoAttribute:
            # Lookup the attribute definition
            atr_def = self._db.get_attribute_definition_by_name(name)

            # only attributes with message as owner are valid, name is also
            # unique accross all attributes so it is enough to check this one
            # for owner
            if atr_def.owner != AttributeOwner.MESSAGE:
                raise KvdWrongOwner()
            value = atr_def.definition.default
        else:
            attribute = Attribute(self._db, ah)
            value = attribute.value
            # if the attribute was an EnumAttribute, find the value
            try:
                value = value.value
            except AttributeError:
                pass
        return value

    def get_signal(self, name):
        """Find signal in message by name."""
        return self.get_signal_by_name(name)

    def get_signal_by_name(self, name):
        """Find signal in message by name."""
        sh = ct.c_void_p(None)
        dll.kvaDbGetSignalByName(self._handle, name.encode('utf-8'), ct.byref(sh))
        signal = _signal_object(self._db, self, sh)
        return signal

    def new_signal(
        self,
        name,
        type=SignalType.UNSIGNED,
        byte_order=SignalByteOrder.INTEL,
        mode=SignalMultiplexMode.SIGNAL,
        representation=None,
        size=None,
        scaling=None,
        limits=None,
        unit=None,
        comment=None,
        enums=None,
    ):
        """Create and add a new signal to the message."""
        sh = ct.c_void_p(None)
        dll.kvaDbAddSignal(self._handle, ct.byref(sh))
        if type > SignalType._ENUM_SEPARATOR:
            type -= SignalType._ENUM_SEPARATOR
            signal = EnumSignal(
                self._db,
                self,
                sh,
                name,
                type,
                byte_order,
                mode,
                size,
                scaling,
                limits,
                unit,
                comment,
                enums,
            )
        else:
            signal = Signal(
                self._db,
                self,
                sh,
                name=name,
                type=type,
                byte_order=byte_order,
                mode=mode,
                representation=representation,
                size=size,
                scaling=scaling,
                limits=limits,
                unit=unit,
                comment=comment,
            )
        return signal

    def set_attribute_value(self, name, value):
        """Set value of attribute 'name' on message.

        If no attribute called 'name' is set on message, attach a message
        attribute from the database attribute definition first.

        """
        ah = ct.c_void_p()

        # Try and find attribute on message
        try:
            dll.kvaDbGetMsgAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        except KvdNoAttribute:
            # If no attribute was found, lookup the attribute definition and
            # add a new attribute to the message
            attrib_def = self._db.get_attribute_definition_by_name(name)
            dll.kvaDbAddMsgAttribute(self._handle, attrib_def._handle, ct.byref(ah))
        # Set the value in the message attribute
        attribute = Attribute(self._db, ah)
        attribute.value = value

    def signals(self):
        """Return a generator of all signals in message."""
        sh = ct.c_void_p(None)
        try:
            dll.kvaDbGetFirstSignal(self._handle, ct.byref(sh))
        except (KvdNoSignal, KvdNoMessage):
            # KvdNoMessage is reported with older (5.22?) dlls
            return
        while sh.value is not None:
            yield _signal_object(self._db, self, sh)
            sh = ct.c_void_p()
            try:
                dll.kvaDbGetNextSignal(self._handle, ct.byref(sh))
            except (KvdNoSignal, KvdNoMessage):
                # KvdNoMessage is reported with older (5.22?) dlls
                return

    @property
    def canflags(self):
        """`.canlib.MessageFlag`: Relevant message attributes expressed as `.canlib.MessageFlag`

        Note that `.canlib.MessageFlag.BRS` will never be returned for non-CAN
        FD frames, even though the CANFD_BRS attribute was set in the .dbc file.

        .. versionadded:: 1.21

        """
        c_flags = ct.c_uint(0)
        dll.kvaDbGetCanMsgFlags(self._handle, ct.byref(c_flags))
        return CanMessageFlag(c_flags.value)

    @property
    def comment(self):
        """`str`: Message comment"""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetMsgComment(self._handle, buf, ct.sizeof(buf))
        try:
            comment = buf.value.decode('utf-8')
        except UnicodeDecodeError:
            comment = buf.value.decode('cp1252')
        return comment

    @comment.setter
    def comment(self, value):
        dll.kvaDbSetMsgComment(self._handle, value.encode('utf-8'))

    @property
    def dlc(self):
        """`int`: The message dlc"""
        c_dlc = ct.c_int(0)
        dll.kvaDbGetMsgDlc(self._handle, ct.byref(c_dlc))
        return c_dlc.value

    @dlc.setter
    def dlc(self, dlc):
        dll.kvaDbSetMsgDlc(self._handle, dlc)

    @property
    def id(self):
        """`int`: The message identifier"""
        c_id = ct.c_uint(0)
        dll.kvaDbGetMsgIdEx(self._handle, ct.byref(c_id))
        return c_id.value

    @id.setter
    def id(self, value):
        dll.kvaDbSetMsgIdEx(self._handle, value)

    @property
    def flags(self):
        """`MessageFlag`: The message flags"""
        c_flags = ct.c_uint(0)
        dll.kvaDbGetMsgFlags(self._handle, ct.byref(c_flags))
        try:
            # There is no guarantee the flags from the dbc file will be valid
            # MessageFlags
            return MessageFlag(c_flags.value)
        except ValueError:
            return c_flags.value

    @flags.setter
    def flags(self, value):
        """Set the message flags."""
        dll.kvaDbSetMsgFlags(self._handle, value)

    @property
    def name(self):
        """`str`: The message name"""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetMsgName(self._handle, buf, ct.sizeof(buf))
        return buf.value.decode('utf-8')

    @name.setter
    def name(self, value):
        dll.kvaDbSetMsgName(self._handle, value.encode('utf-8'))

    @property
    def qualified_name(self):
        """`str`: The qualified message name

        Returns database and message names separated by a dot.
        """
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetMsgQualifiedName(self._handle, buf, ct.sizeof(buf))
        return buf.value.decode('utf-8')

    @property
    def send_node(self):
        """`Node`: The send node for this message."""
        nh = ct.c_void_p()
        dll.kvaDbGetMsgSendNode(self._handle, ct.byref(nh))
        node = Node(self._db, nh)
        return node

    @send_node.setter
    def send_node(self, value):
        dll.kvaDbSetMsgSendNode(self._handle, value._handle)
