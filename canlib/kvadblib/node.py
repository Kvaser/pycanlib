import ctypes as ct

from .attribute import Attribute
from .enums import AttributeOwner
from .exceptions import KvdNoAttribute, KvdWrongOwner
from .wrapper import dll


class Node:
    """Database Node"""

    def __init__(self, db, handle, name=None, comment=None):
        self._handle = handle
        self._db = db  # used to lookup attribute definitions
        if name is not None:
            self.name = name
        if comment is not None:
            self.comment = comment

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.comment != other.comment:
            return False
        return True

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return f"Node(name='{self.name}, comment={self.comment}')"

    def attributes(self):
        """Return a generator over all message attributes."""
        ah = None
        nah = ct.c_void_p()
        try:
            dll.kvaDbGetFirstNodeAttribute(self._handle, ct.byref(nah))
        except KvdNoAttribute:
            return
        while nah.value is not None:
            ah, nah = nah, ct.c_void_p()
            yield Attribute(self, ah)
            try:
                dll.kvaDbGetNextAttribute(ah, ct.byref(nah))
            except KvdNoAttribute:
                return

    def delete_attribute(self, name):
        """Delete attribute from node."""
        ah = ct.c_void_p()
        dll.kvaDbGetNodeAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        dll.kvaDbDeleteNodeAttribute(self._handle, ah)

    def get_attribute_value(self, name):
        """Return attribute value

        If the attribute is not set on the message, we return the attribute
        definition default value.

        """
        ah = ct.c_void_p()

        # Try and find attribute on node
        try:
            dll.kvaDbGetNodeAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        except KvdNoAttribute:
            # Lookup the attribute definition
            atr_def = self._db.get_attribute_definition_by_name(name)

            # only attributes with node as owner are valid, name is also
            # unique accross all attributes so it is enough to check this one
            # for owner
            if atr_def.owner != AttributeOwner.NODE:
                raise KvdWrongOwner()
            value = atr_def.definition.default
        else:
            attribute = Attribute(self._db, ah)
            value = attribute.value
        return value

    def set_attribute_value(self, name, value):
        """Set value of attribute 'name' on node.

        If no attribute called 'name' is set on node, attach a node
        attribute from the database attribute definition first.

        """
        ah = ct.c_void_p()

        # Try and find attribute on node
        try:
            dll.kvaDbGetNodeAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        except KvdNoAttribute:
            # If no attribute was found, lookup the attribute definition and
            # add a new attribute to the node
            attrib_def = self._db.get_attribute_definition_by_name(name)
            dll.kvaDbAddNodeAttribute(self._handle, attrib_def._handle, ct.byref(ah))
        # Set the value in the node attribute
        attribute = Attribute(self._db, ah)
        attribute.value = value

    @property
    def comment(self):
        """`str`: The node's comment"""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetNodeComment(self._handle, buf, ct.sizeof(buf))
        return buf.value.decode('utf-8')

    @comment.setter
    def comment(self, value):
        dll.kvaDbSetNodeComment(self._handle, value.encode('utf-8'))

    @property
    def name(self):
        """`str`: The node's name"""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetNodeName(self._handle, buf, ct.sizeof(buf))
        return buf.value.decode('utf-8')

    @name.setter
    def name(self, value):
        dll.kvaDbSetNodeName(self._handle, value.encode('utf-8'))
