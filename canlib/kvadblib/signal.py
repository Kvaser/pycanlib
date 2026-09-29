"""Wrapper for Kvaser Database API (kvaDbLib)."""

import ctypes as ct
from collections import namedtuple

from .attribute import Attribute
from .bound_signal import BoundSignal
from .enums import (AttributeOwner, SignalByteOrder, SignalType)
from .exceptions import KvdNoAttribute, KvdWrongOwner
from .wrapper import dll

ValueLimits = namedtuple('ValueLimits', 'min max')
ValueScaling = namedtuple('ValueScaling', 'factor offset')
ValueSize = namedtuple('ValueSize', 'startbit length')


class Signal:
    """Database signal, holds meta data about a signal"""

    def __init__(
        self,
        db,
        message,
        sh,
        name=None,
        type=None,
        byte_order=None,
        mode=None,
        representation=None,
        size=None,
        scaling=None,
        limits=None,
        unit=None,
        comment=None,
    ):
        self._db = db  # used to lookup attribute definitions
        self._handle = sh
        self.message = message  # Parent message
        # Any property that is set at creation time needs to be written to the signal object.
        # qqqmac loop through attributes instead of keeping this "manual list"?
        if byte_order is not None:
            self.byte_order = byte_order
        if mode is not None:
            self.mode = mode
        if scaling is not None:
            self.scaling = scaling
        if comment is not None:
            self.comment = comment
        if limits is not None:
            self.limits = limits
        if name is not None:
            self.name = name
        if representation is not None:
            self.representation = representation
        if size is not None:
            self.size = size
        if type is not None:
            self.type = type
        if unit is not None:
            self.unit = unit

    def __eq__(self, other):
        attrs = 'name type byte_order mode size scaling limits unit comment'.split()
        return all(getattr(self, a) == getattr(other, a) for a in attrs)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        # __repr__ should never do any calls to the dll, so this needs to be done in __str__
        return (
            "Signal(name={!r}, type={!r}, byte_order={!r}, mode={!r}, size={!r}, "
            "scaling={!r}, limits={!r}, unit={!r}, comment={!r})".format(
                self.name,
                self.type,
                self.byte_order,
                self.mode,
                self.size,
                self.scaling,
                self.limits,
                self.unit,
                self.comment,
            )
        )

    def attributes(self):
        """Return a generator over all signal attributes."""
        ah = None
        nah = ct.c_void_p()
        try:
            dll.kvaDbGetFirstSignalAttribute(self._handle, ct.byref(nah))
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
        """Bind this signal to a frame

        Creates a new BoundSignal object representing this signal bound to
        the given Frame object, or a new Frame object if `frame` is `None`..

        """
        return BoundSignal(self, frame or self.message.asframe())

    def add_node(self, node):
        """Add receiving node to signal."""
        dll.kvaDbAddReceiveNodeToSignal(self._handle, node._handle)

    def data_from(self, can_data, phys=None, raw=None):
        """Convert a raw or physical value into CAN data bytes."""
        c_buf = (ct.c_char * len(can_data)).from_buffer_copy(can_data)
        if phys is not None:
            c_phys = ct.c_double(phys)
            dll.kvaDbStoreSignalValuePhys(self._handle, c_buf, ct.sizeof(c_buf), c_phys)
        if raw is not None:
            c_raw = ct.c_uint64(raw)
            dll.kvaDbStoreSignalValueRaw64(self._handle, c_buf, ct.sizeof(c_buf), c_raw)
        return bytearray(c_buf)

    def delete_attribute(self, name):
        """Delete attribute from signal."""
        ah = ct.c_void_p()
        dll.kvaDbGetSignalAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        dll.kvaDbDeleteSignalAttribute(self._handle, ah)

    def get_attribute_value(self, name):
        """Return attribute value

        If the attribute is not set on the signal, we return the attribute
        definition default value.

        """
        ah = ct.c_void_p()

        # Try and find attribute on signal
        try:
            dll.kvaDbGetSignalAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        except KvdNoAttribute:
            # Lookup the attribute definition
            atr_def = self._db.get_attribute_definition_by_name(name)

            # only attributes with signal as owner are valid, name is also unique
            # accross all attributes so it is enough to check this one for owner
            if atr_def.owner != AttributeOwner.SIGNAL:
                raise KvdWrongOwner()
            value = atr_def.definition.default
        else:
            attribute = Attribute(self._db, ah)
            value = attribute.value
        return value

    def nodes(self):
        """Return a generator over all receiving nodes of the signal."""
        for node in self._db.nodes():
            if self._db.node_in_signal(node, self):
                yield node

    def remove_node(self, node):
        """Remove receiving node from signal."""
        dll.kvaDbRemoveReceiveNodeFromSignal(self._handle, node._handle)

    def set_attribute_value(self, name, value):
        """Set value of attribute 'name' on signal.

        If no attribute called 'name' is set on signal, attach a signal
        attribute from the database attribute definition first.

        """
        ah = ct.c_void_p()

        # Try and find attribute on signal
        try:
            dll.kvaDbGetSignalAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        except KvdNoAttribute:
            # If no attribute was found, lookup the attribute definition and
            # add a new attribute to the message
            attrib_def = self._db.get_attribute_definition_by_name(name)
            dll.kvaDbAddSignalAttribute(self._handle, attrib_def._handle, ct.byref(ah))
        # Set the value in the signal attribute
        attribute = Attribute(self._db, ah)
        attribute.value = value

    @property
    def comment(self):
        """`str`: Get the signal comment."""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetSignalComment(self._handle, buf, ct.sizeof(buf))
        try:
            comment = buf.value.decode('utf-8')
        except UnicodeDecodeError:
            comment = buf.value.decode('cp1252')
        return comment

    @comment.setter
    def comment(self, value):
        """`str`: Set the signal comment."""
        dll.kvaDbSetSignalComment(self._handle, value.encode('utf-8'))

    @property
    def byte_order(self):
        """`SignalByteOrder`: Get the signal byte order encoding."""
        t = ct.c_uint(0)
        dll.kvaDbGetSignalEncoding(self._handle, ct.byref(t))
        try:
            # There is no guarantee the flags from the dbc file will be valid
            # MessageFlags
            return SignalByteOrder(t.value)
        except ValueError:
            return t.value

    @byte_order.setter
    def byte_order(self, value):
        """Set the signal byte order encoding."""
        dll.kvaDbSetSignalEncoding(self._handle, value)

    @property
    def name(self):
        """`str`: Get the signal name."""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetSignalName(self._handle, buf, ct.sizeof(buf))
        return (buf.value).decode('utf-8')

    @name.setter
    def name(self, value):
        """Set the signal name."""
        dll.kvaDbSetSignalName(self._handle, value.encode('utf-8'))

    @property
    def qualified_name(self):
        """`str`: Get the qualified signal name.

        Returns database, message and signal names separated by dots.
        """
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetSignalQualifiedName(self._handle, buf, ct.sizeof(buf))
        return buf.value.decode('utf-8')

    def phys_from(self, can_data):
        """Return signals physical value from data"""
        c_phys = ct.c_double()
        c_buf = (ct.c_char * len(can_data)).from_buffer_copy(can_data)
        dll.kvaDbRetrieveSignalValuePhys(self._handle, ct.byref(c_phys), c_buf, ct.sizeof(c_buf))
        return c_phys.value

    def raw_from(self, can_data):
        """Return signals raw value from data"""
        raw = ct.c_uint64()
        c_buf = (ct.c_char * len(can_data)).from_buffer_copy(can_data)
        dll.kvaDbRetrieveSignalValueRaw64(self._handle, ct.byref(raw), c_buf, ct.sizeof(c_buf))
        return raw.value

    @property
    def scaling(self):
        """`ValueScaling`: Get the signals factor and offset"""
        c_factor = ct.c_double(0)
        c_offset = ct.c_double(0)
        dll.kvaDbGetSignalValueScaling(self._handle, ct.byref(c_factor), ct.byref(c_offset))
        return ValueScaling(factor=c_factor.value, offset=c_offset.value)

    @scaling.setter
    def scaling(self, value):
        """`ValueScaling`: Set the signals factor and offset"""
        dll.kvaDbSetSignalValueScaling(self._handle, value.factor, value.offset)

    @property
    def size(self):
        """`ValueSize`: Get the signals startbit and length"""
        c_startbit = ct.c_int(0)
        c_length = ct.c_int(0)
        dll.kvaDbGetSignalValueSize(self._handle, ct.byref(c_startbit), ct.byref(c_length))
        return ValueSize(startbit=c_startbit.value, length=c_length.value)

    @size.setter
    def size(self, value):
        """Set the signals startbit and length.

        Args:
            value (`ValueSize`

        """
        dll.kvaDbSetSignalValueSize(self._handle, value.startbit, value.length)

    @property
    def type(self):
        """`SignalType`: Get the signal representation type."""
        t = ct.c_uint(-1)
        dll.kvaDbGetSignalRepresentationType(self._handle, ct.byref(t))
        try:
            # There is no guarantee the flags from the dbc file will be valid
            # MessageFlags
            return SignalType(t.value)
        except ValueError:
            return t.value

    @type.setter
    def type(self, value):
        """Set the signal representation type."""
        dll.kvaDbSetSignalRepresentationType(self._handle, value)

    @property
    def unit(self):
        """`str`: Get the signal unit"""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetSignalUnit(self._handle, buf, ct.sizeof(buf))
        try:
            unit = buf.value.decode('utf-8')
        except UnicodeDecodeError:
            unit = buf.value.decode('cp1252')
        return unit

    @unit.setter
    def unit(self, value):
        """Set the signal unit (str)."""
        dll.kvaDbSetSignalUnit(self._handle, value.encode('utf-8'))

    @property
    def limits(self):
        """`ValueLimits`: Get message min and max values"""
        c_min = ct.c_double(0)
        c_max = ct.c_double(0)
        dll.kvaDbGetSignalValueLimits(self._handle, ct.byref(c_min), ct.byref(c_max))
        return ValueLimits(min=c_min.value, max=c_max.value)

    @limits.setter
    def limits(self, value):
        """Get message min and max values.

        Args:
            value (`ValueLimits`)

        """
        dll.kvaDbSetSignalValueLimits(self._handle, value.min, value.max)

    @property
    def mode(self):
        c_mux = ct.c_int()
        dll.kvaDbGetSignalMode(self._handle, ct.byref(c_mux))
        return c_mux.value

    @mode.setter
    def mode(self, value):
        c_mux = ct.c_int(value)
        dll.kvaDbSetSignalMode(self._handle, c_mux)


class EnumSignal(Signal):
    """Database signal of type enum, holds meta data about a signal.

    .. versionchanged:: 1.17
        default settings byte_order=SignalByteOrder.INTEL and mode=SignalMultiplexMode.SIGNAL chaged to None.

    """

    def __init__(
        self,
        db,
        message,
        sh,
        name=None,
        type=None,
        byte_order=None,
        mode=None,
        size=None,
        scaling=None,
        limits=None,
        unit=None,
        comment=None,
        enums=None,
    ):
        super().__init__(
            db,
            message=message,
            sh=sh,
            name=name,
            type=type,
            byte_order=byte_order,
            mode=mode,
            size=size,
            scaling=scaling,
            limits=limits,
            unit=unit,
            comment=comment,
        )
        if enums is not None:
            self.add_enum_definition(enums)

    def _enum_handles(self):
        """Return enum generator"""
        eh = ct.c_void_p(None)
        try:
            dll.kvaDbGetFirstEnumValue(self._handle, ct.byref(eh))
        except KvdNoAttribute:
            return
        while eh.value is not None:
            yield eh.value
            try:
                dll.kvaDbGetNextEnumValue(self._handle, ct.byref(eh))
            except KvdNoAttribute:
                return

    def _delete_enum(self, eh):
        """Delete enum assosiated with handle eh."""
        c_eh = ct.c_void_p(eh)
        dll.kvaDbDeleteEnumValue(self._handle, c_eh)

    def add_enum_definition(self, enums):
        """Add enums dictionary to definition."""
        for key, value in enums.items():
            c_key = ct.create_string_buffer(key.encode('utf-8'))
            c_value = ct.c_int(value)
            dll.kvaDbAddEnumValue(self._handle, c_value, c_key)

    @property
    def enums(self):
        """`dict`: Signal enum definition dictionary"""
        enums = {}
        c_val = ct.c_int()
        buf = ct.create_string_buffer(255)

        for eh in self._enum_handles():
            c_eh = ct.c_void_p(eh)
            dll.kvaDbGetEnumValue(c_eh, ct.byref(c_val), buf, ct.sizeof(buf))
            enums[buf.value.decode('utf-8')] = c_val.value
        return enums

    @enums.setter
    def enums(self, enums):
        # Deleting affects the generator, so get the whole list here
        for eh in list(self._enum_handles()):
            self._delete_enum(eh)
        self.add_enum_definition(enums)

    def __eq__(self, other):
        sup = super().__eq__(other)
        if sup is NotImplemented:
            return sup
        else:
            return sup and self.enums == other.enums
