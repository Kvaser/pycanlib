import ctypes as ct
from collections import namedtuple

from . import enums
from .exceptions import KvdNoAttribute
from .wrapper import dll

MinMaxDefinition = namedtuple('MinMaxDefinition', 'default min max')
"""Attribute definition for attributes defined using default, min and max."""

DefaultDefinition = namedtuple('DefaultDefinition', 'default')
"""Attribute definition for attributes defined using only default."""

EnumDefaultDefinition = namedtuple('EnumDefaultDefinition', 'default enums')
"""Attribute definition for enumeration attributes.

Holds a definition using default and key-value pairs.
"""


class AttributeDefinition:
    """Factory for creating different types of attribute definitions.

    This class is also the base class and thus contains all common properties.
    """

    def __new__(cls, db, handle, definition=None):
        """Create attribute definition class depending on type."""
        if cls != AttributeDefinition:
            obj = super().__new__(cls)
            return obj
        type = ct.c_int()
        dll.kvaDbGetAttributeDefinitionType(handle, ct.byref(type))
        if type.value == enums.AttributeType.INTEGER:
            cls_ = IntegerDefinition
        elif type.value == enums.AttributeType.FLOAT:
            cls_ = FloatDefinition
        elif type.value == enums.AttributeType.STRING:
            cls_ = StringDefinition
        elif type.value == enums.AttributeType.ENUM:
            cls_ = EnumDefinition
        elif type.value == enums.AttributeType.HEX:
            cls_ = HexDefinition
        else:
            type = enums.AttributeType(type.value)
            raise NotImplementedError(f'{type.name} not implemented')

        return cls_.__new__(cls_, db, handle, definition)

    def __init__(self, db, handle):
        self._handle = handle
        self._db = db

    def __repr__(self):
        txt = "<{}(name='{}', definition={}, owner={!r})>".format(
            self.__class__.__name__, self.name, self.definition, self.owner
        )
        return txt

    @property
    def name(self):
        """`str`: Name of attribute definition."""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetAttributeDefinitionName(self._handle, buf, ct.sizeof(buf))
        return buf.value.decode('utf-8')

    @name.setter
    def name(self, value):
        dll.kvaDbSetAttributeDefinitionName(self._handle, value.encode('utf-8'))

    @property
    def owner(self):
        """`AttributeOwner`: Return attribute owner"""
        owner = ct.c_int(0)
        dll.kvaDbGetAttributeDefinitionOwner(self._handle, ct.byref(owner))
        return enums.AttributeOwner(owner.value)

    @owner.setter
    def owner(self, owner):
        dll.kvaDbSetAttributeDefinitionOwner(self._handle, owner)


class FloatDefinition(AttributeDefinition):
    """Definition of a float attribute.

    Args:
        db (`Dbc`): Database that holds attribute definitions
        definition (`MinMaxDefinition`): Min, max and default values
    """
    def __init__(self, db, handle, definition=None):
        super().__init__(db, handle)
        # self._ah = None
        if definition is not None:
            self.definition = definition

    @property
    def definition(self):
        """`MinMaxDefinition`: Attribute definition"""
        default = ct.c_float()
        min = ct.c_float()
        max = ct.c_float()
        dll.kvaDbGetAttributeDefinitionFloat(self._handle, default, min, max)
        definition = MinMaxDefinition(default=default.value, min=min.value, max=max.value)
        return definition

    @definition.setter
    def definition(self, value):
        dll.kvaDbSetAttributeDefinitionFloat(self._handle, value.default, value.min, value.max)


class IntegerDefinition(AttributeDefinition):
    """Definition of an integer attribute.

    Args:
        db (`Dbc`): Database that holds attribute definitions
        definition (`MinMaxDefinition`): Min, max and default values
    """
    def __init__(self, db, handle, definition=None):
        super().__init__(db, handle)
        if definition is not None:
            self.definition = definition

    @property
    def definition(self):
        """`MinMaxDefinition`: Return attribute definition"""
        default = ct.c_int()
        min = ct.c_int()
        max = ct.c_int()
        dll.kvaDbGetAttributeDefinitionInt(self._handle, default, min, max)
        definition = MinMaxDefinition(default=default.value, min=min.value, max=max.value)
        return definition

    @definition.setter
    def definition(self, value):
        dll.kvaDbSetAttributeDefinitionInt(self._handle, value.default, value.min, value.max)


class HexDefinition(IntegerDefinition):
    """Definition of an hex attribute.

    Args:
        db (`Dbc`): Database that holds attribute definitions
        definition (`MinMaxDefinition`): Min, max and default values

    .. versionadded:: 1.20

    """
    pass


class StringDefinition(AttributeDefinition):
    """Definition of a string attribute.

    Args:
        db (`Dbc`): Database that holds attribute definitions
        definition (`DefaultDefinition`): default value
    """
    def __init__(self, db, handle, definition=None):
        super().__init__(db, handle)
        if definition is not None:
            self.definition = definition

    @property
    def definition(self):
        """`DefaultDefinition`: Return attribute definition"""
        c_default = ct.create_string_buffer(255)
        dll.kvaDbGetAttributeDefinitionString(self._handle, c_default, ct.sizeof(c_default))
        definition = DefaultDefinition(default=c_default.value.decode('utf-8'))
        return definition

    @definition.setter
    def definition(self, value):
        c_default = ct.create_string_buffer(value.default.encode('utf-8'))
        dll.kvaDbSetAttributeDefinitionString(self._handle, c_default)


class EnumDefinition(AttributeDefinition):
    """Definition of an enum attribute.

    Args:
        db (`Dbc`): Database that holds attribute definitions
        definition (`EnumDefaultDefinition`): default value and enums

    """
    def __init__(self, db, handle, definition=None):
        super().__init__(db, handle)
        if definition is not None:
            self.definition = definition

    def add_enum_definition(self, enums):
        """Add enum definitions.

        Args:
            enums (dict): key - value pair(s), example: {'empty': 0}
        """
        for key, value in enums.items():
            c_key = ct.create_string_buffer(key.encode('utf-8'))
            c_value = ct.c_int(value)
            dll.kvaDbAddAttributeDefinitionEnum(self._handle, c_key, c_value)

    def _enums(self):
        """Return a generator of all enum key - value pair(s)

        .. versionadded:: 1.6

        """
        buf = ct.create_string_buffer(255)
        c_value = ct.c_int()
        c_buf_size = ct.c_size_t(ct.sizeof(buf))
        try:
            dll.kvaDbGetAttributeDefinitionEnumFirst(
                self._handle, ct.byref(c_value), buf, ct.byref(c_buf_size)
            )
        except KvdNoAttribute:
            return
        while True:
            yield (buf.value.decode('utf-8'), c_value.value)
            try:
                dll.kvaDbGetAttributeDefinitionEnumNext(
                    self._handle, ct.byref(c_value), buf, ct.byref(c_buf_size)
                )
            except KvdNoAttribute:
                return

    @property
    def definition(self):
        """`EnumDefaultDefinition`: Return attribute definition

        .. versionchanged:: 1.6

        """
        c_default = ct.c_int()
        dll.kvaDbGetAttributeDefinitionEnumeration(self._handle, ct.byref(c_default))
        enums = dict(list(self._enums()))
        definition = EnumDefaultDefinition(default=c_default.value, enums=enums)
        return definition

    @definition.setter
    def definition(self, value):
        dll.kvaDbSetAttributeDefinitionEnumDefault(self._handle, value.default)
        self.add_enum_definition(value.enums)
