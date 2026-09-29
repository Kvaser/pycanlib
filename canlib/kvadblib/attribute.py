import ctypes as ct
from collections import namedtuple

from .enums import AttributeType
from .wrapper import dll

EnumValue = namedtuple('EnumValue', 'name value')
"""Holds an Enum key - value pair"""


class Attribute:
    """Factory for creating different types of attributes.

    This class is also the base class and thus contains all common properties.
    """

    def __new__(cls, db, handle):
        """Create new attribute class depending on type."""
        if cls != Attribute:
            obj = super().__new__(cls)
            return obj
        type = ct.c_int()
        dll.kvaDbGetAttributeType(handle, ct.byref(type))
        if type.value == AttributeType.INTEGER:
            return IntegerAttribute(db, handle)
        elif type.value == AttributeType.FLOAT:
            return FloatAttribute(db, handle)
        elif type.value == AttributeType.ENUM:
            return EnumAttribute(db, handle)
        elif type.value == AttributeType.STRING:
            return StringAttribute(db, handle)
        elif type.value == AttributeType.HEX:
            return HexAttribute(db, handle)
        else:
            type = AttributeType(type.value)
            raise NotImplementedError(f'{type.name} not implemented')

    def __init__(self, db, handle):
        self._db = db
        self._handle = handle

    def __repr__(self):
        txt = f"<{self.__class__.__name__}(name='{self.name}', value={self.value!r})>"
        return txt

    @property
    def name(self):
        """`str`: Name of attribute."""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetAttributeName(self._handle, buf, ct.sizeof(buf))
        return buf.value.decode('utf-8')

    @property
    def value(self):
        """Attribute value"""
        return self._get_value()

    @value.setter
    def value(self, value):
        self._set_value(value)


class IntegerAttribute(Attribute):
    """Attribute of type Integer."""

    def _get_value(self):
        val = ct.c_int()
        dll.kvaDbGetAttributeValueInt(self._handle, ct.byref(val))
        return val.value

    def _set_value(self, value):
        dll.kvaDbSetAttributeValueInt(self._handle, value)


class HexAttribute(IntegerAttribute):
    """Attribute of type Hex.

    .. versionadded:: 1.20

    """
    pass


class FloatAttribute(Attribute):
    """Attribute of type Float."""

    def _get_value(self):
        val = ct.c_float()
        dll.kvaDbGetAttributeValueFloat(self._handle, ct.byref(val))
        return val.value

    def _set_value(self, value):
        dll.kvaDbSetAttributeValueFloat(self._handle, value)


class EnumAttribute(Attribute):
    """Attribute of type Enum."""

    def _get_value(self):
        val = ct.c_int()
        dll.kvaDbGetAttributeValueEnumeration(self._handle, ct.byref(val))
        return EnumValue(name='', value=val.value)

    def _set_value(self, value):
        dll.kvaDbSetAttributeValueEnumeration(self._handle, value)


class StringAttribute(Attribute):
    """Attribute of type String"""

    def _get_value(self):
        val = ct.create_string_buffer(255)
        dll.kvaDbGetAttributeValueString(self._handle, val, ct.sizeof(val))
        return val.value.decode('utf8')

    def _set_value(self, value):
        value = ct.create_string_buffer(value.encode('utf8'))
        dll.kvaDbSetAttributeValueString(self._handle, value, ct.sizeof(value))
