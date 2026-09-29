"""Wrapper for Kvaser Database API (kvaDbLib).  For more info, see the kvaDbLib
   help files which are availible in the CANlib SDK.
   https://www.kvaser.com/developer/canlib-sdk/

"""

import ctypes as ct

from canlib.canlib.enums import MessageFlag as canlib_MessageFlag

from .attribute import Attribute
from .attributedef import AttributeDefinition
from .enums import AttributeOwner, MessageFlag, ProtocolType
from .exceptions import (KvdDbFileParse, KvdNoAttribute, KvdNoMessage,
                         KvdNoNode, KvdOnlyOneAllowed, KvdWrongOwner)
from .message import Message
from .node import Node
from .wrapper import dll, get_last_parse_error

DATABASE_FLAG_J1939 = 0x0001  #: Flag indicating that the database uses the J1939 protocol.


class Dbc:
    """Holds a dbc database.


    There are three ways to create a database:

    1. To load data from an existing database file, only set filename to
       the database filename.

    2. To add an empty database, set only name.

    3. To load data from an existing database file and give it a new name, set
       name to the new name and filename to the existing database filename.

    Either a name or a filename must be given.

    Args:
        filename (str, optional): The existing database file is read.
        name (str, optional): The database name will be set.

    Raises:
        KvdDbFileParse: If the database file can't be parsed.

    When parsing a database file fails, `get_last_parse_error` can be called::

            try:
                kvadblib.Dbc(filename="database.dbc")
            except kvadblib.KvdDbFileParse:
                print(kvadblib.get_last_parse_error())


    .. versionchanged:: 1.10

        `Dbc` now raises specific errors depending on the situation.

    """

    def __init__(self, filename=None, name=None, protocol=None):
        if name is None and filename is None:
            raise TypeError('Either a name or filename must to be given.')

        self._handle = None
        handle = ct.c_void_p(None)
        dll.kvaDbOpen(ct.byref(handle))
        self._handle = handle
        if name:
            name = name.encode('utf-8')
        if filename:
            # use str() here to allow for Path objects as filename
            filename = str(filename).encode('utf-8')
        try:
            dll.kvaDbCreate(self._handle, name, filename)
        except KvdDbFileParse:
            print(get_last_parse_error())
            raise

        # set default protocol to CAN
        if protocol is not None:
            self.protocol = protocol
        if protocol is None and self.protocol == ProtocolType.UNKNOWN:
            self.protocol = ProtocolType.CAN

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        """Return a generator of all normal database messages.

        Equivalent to Dbc.messages(show_all=False).
        """

        return self.messages(show_all=False)

    def __len__(self):
        """Returns number of messages in database."""
        return sum(1 for _ in self)

    def __str__(self):
        return "Dbc {}: flags:{}, protocol:{}, messages:{}".format(
            self.name, self.flags, self.protocol.name, len(self)
        )

    def attribute_definitions(self):
        """Return a generator over all database attribute definitions."""
        adh = None
        nadh = ct.c_void_p()

        try:
            dll.kvaDbGetFirstAttributeDefinition(self._handle, ct.byref(nadh))
        except KvdNoAttribute:
            return
        while nadh.value is not None:
            adh, nadh = nadh, ct.c_void_p()
            yield AttributeDefinition(self, adh)
            try:
                dll.kvaDbGetNextAttributeDefinition(adh, ct.byref(nadh))
            except KvdNoAttribute:
                return
        return

    def attributes(self):
        """Return a generator over all database attributes.

        .. versionadded:: 1.6

        """
        ah = None
        nah = ct.c_void_p()
        try:
            dll.kvaDbGetFirstAttribute(self._handle, ct.byref(nah))
        except KvdNoAttribute:
            return
        while nah.value is not None:
            ah, nah = nah, ct.c_void_p()
            yield Attribute(self, ah)
            try:
                dll.kvaDbGetNextAttribute(ah, ct.byref(nah))
            except KvdNoAttribute:
                return

    def close(self):
        """Close an open database handle."""
        if self._handle:
            dll.kvaDbClose(self._handle)

    def delete_attribute(self, name):
        """Delete attribute from database.

        .. versionadded:: 1.6

        """
        ah = ct.c_void_p()
        dll.kvaDbGetAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        dll.kvaDbDeleteAttribute(self._handle, ah)

    def delete_attribute_definition(self, name):
        """Delete attribute definition from database.

        .. versionadded:: 1.7

        """
        adh = ct.c_void_p(None)
        dll.kvaDbGetAttributeDefinitionByName(self._handle, name.encode('utf-8'), ct.byref(adh))
        dll.kvaDbDeleteAttributeDefinition(self._handle, adh)

    def delete_message(self, message):
        """Delete message from database.

        Args:
            message (`Message`): message to be deleted

        """
        dll.kvaDbDeleteMsg(self._handle, message._handle)

    def delete_node(self, node):
        """Delete node from database.

        Args:
            node (`Node`): node to be deleted

        """
        dll.kvaDbDeleteNode(self._handle, node._handle)

    def get_attribute_definition_by_name(self, name):
        """Find attribute definition using name.

        Args:
            name (str): name of attribute definition

        Returns an attribute definition object depending on type, e.g. if the
        type is AttributeType.INTEGER, an `IntegerAttributeDefinition` is
        returned.

        """
        adh = ct.c_void_p(None)
        dll.kvaDbGetAttributeDefinitionByName(self._handle, name.encode('utf-8'), ct.byref(adh))
        return AttributeDefinition(self, adh)

    def get_attribute_value(self, name):
        """Return attribute value

        If the attribute is not set on the database, we return the attribute
        definition default value.

        .. versionadded:: 1.6

        """
        ah = ct.c_void_p()

        # Try and find attribute on message
        try:
            dll.kvaDbGetAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        except KvdNoAttribute:
            # Lookup the attribute definition
            atr_def = self.get_attribute_definition_by_name(name)

            # only attributes with database as owner are valid, name is also
            # unique accross all attributes so it is enough to check this one
            # for owner
            if atr_def.owner != AttributeOwner.DB:
                raise KvdWrongOwner()
            value = atr_def.definition.default
        else:
            attribute = Attribute(self, ah)
            value = attribute.value
        return value

    def get_message(self, id=None, name=None):
        """Find message by id or name

        If both id and name is given, both most match.

        Note that bit 31 of the id indicates if the message has an extended id
        or not.

        Args:
            id (int): message id to look for
            name (str): message name to look for

        Returns:
            `Message`

        Raises:
            KvdNoMessage: If no match was found, or if none of `id` and
                `name` were given.

        """
        message = None
        if (id is not None) and (name is not None):
            # Both arguments were given
            message = self.get_message_by_id(id, id & MessageFlag.EXT)
            if message.name == name:
                return message
            else:
                raise KvdNoMessage()
        else:
            if id is not None:
                return self.get_message_by_id(id, id & MessageFlag.EXT)
            else:
                return self.get_message_by_name(name)

    def get_message_by_id(self, id, flags):
        """Find message by id.

        Args:
            id (int): message id to look for
            flags (int): message flags, e.g. `kvadblib.MessageFlag.EXT`
                        (Note that `kvadblib.MessageFlag.EXT` != `canlib.MessageFlag.EXT`)

        Returns:
            `Message`

        Raises:
            KvdNoMessage: If no match was found.

        """
        # Still using legacy function kvaDbGetMsgById() in order to be
        # backwards compliant.
        flags &= MessageFlag.EXT
        id |= flags

        mh = ct.c_void_p(None)

        dll.kvaDbGetMsgById(self._handle, id, ct.byref(mh))
        message = Message(db=self, handle=mh)
        return message

    def get_message_by_name(self, name):
        """Find message by name

        Args:
            name (str): message name to look for

        Returns:
            `Message`

        Raises:
            KvdNoMessage: If no match was found.

        """
        mh = ct.c_void_p(None)
        dll.kvaDbGetMsgByName(self._handle, name.encode('utf-8'), ct.byref(mh))
        message = Message(self, mh)
        return message

    def get_message_by_pgn(self, can_id):
        """Find message using the PGN part of the given CAN id.

        Note:

            The `can_id` must have the `MessageFlag.EXT` flag bit set (bit 31, 0x80000000) ::

                dbc = kvadblib.Dbc("My_j1939_database.dbc")
                can_id = 0xff4200
                can_id |= kvadblib.MessageFlag.EXT
                dbc.get_message_by_pgn(can_id)


        Args:
            can_id (int): CAN id containing PGN to look for

        Returns:
            `Message`

        Raises:
            KvdNoMessage: If no match was found.

        .. versionadded:: 1.18

        """
        mh = ct.c_void_p(None)

        dll.kvaDbGetMsgByPGN(self._handle, can_id, ct.byref(mh))
        message = Message(db=self, handle=mh)
        return message

    def get_node_by_name(self, name):
        """Find node by name

        Args:
            name (str): node name to look for

        Returns:
            `Node`

        Raises:
            KvdNoNode: If no match was found.

        """
        nh = ct.c_void_p(None)
        dll.kvaDbGetNodeByName(self._handle, name.encode('utf-8'), ct.byref(nh))
        return Node(self, nh)

    def messages(self, show_all=True):
        """Return a generator of all database messages.

        If you would like to omit the special message
        'VECTOR__INDEPENDENT_SIG_MSG', which is used to collect removed signals
        under, set show_all to False or use the Dbc iterator directly::

            db = kvadblib.Dbc(filename='mydb.dbc')
            for message in db:
                print(msg)

        Args:

            show_all (`bool`): If true, all messages, including any special
                message such as 'VECTOR__INDEPENDENT_SIG_MSG' will be returned

        .. versionchanged:: 1.8
           Added argument show_all.

        """
        mh = ct.c_void_p(None)
        try:
            dll.kvaDbGetFirstMsg(self._handle, ct.byref(mh))
        except KvdNoMessage:
            return
        while mh.value is not None:
            msg = Message(self, mh)
            # The special message name VECTOR__INDEPENDENT_SIG_MSG is used in
            # .dbc files to collect unused signals into
            # Only return special message if show_all is True
            if show_all or msg.name != 'VECTOR__INDEPENDENT_SIG_MSG':
                yield msg
            mh = ct.c_void_p()
            try:
                dll.kvaDbGetNextMsg(self._handle, ct.byref(mh))
            except KvdNoMessage:
                return

    def interpret(self, frame, j1939=False):
        """Interprets a given `canlib.Frame` object, returning a `BoundMessage`."""
        can_id = frame.id
        flags = 0

        if j1939:
            # When calling get_message_by_pgn, the EXT flag must be attached to the CAN ID
            # Check frame.flags first, since it may be '0'
            # Note that MessageFlag.EXT has different values in canlib vs kvadblib
            if frame.flags and canlib_MessageFlag.EXT in frame.flags:
                can_id |= MessageFlag.EXT
            message = self.get_message_by_pgn(can_id)
            return message.bind(frame)

        # When calling get_message_by_id, the EXT flag must be provided in flags argument
        # Note that MessageFlag.EXT has different values in canlib vs kvadblib
        # Check frame.flags first, since it may be '0'
        if frame.flags and canlib_MessageFlag.EXT in frame.flags:
            flags = flags | MessageFlag.EXT
        # Still using legacy version of get_message_by_id in order to be
        # backwards compliant.
        message = self.get_message_by_id(can_id, flags)
        return message.bind(frame)

    def new_attribute_definition(self, name, owner, type, definition):
        """Create a new attribute definition in the database.

        The owner specify where the attribute is applicable,
        e.g. `AttributeOwner.MESSAGE` specifies that this attribute is
        only applicable on messages (`Message`).

        Args:
            name (str): a unique name.
            owner (`AttributeOwner`): the owner type

        Returns:
            `AttributeDefinition`

        """
        adh = ct.c_void_p(None)
        dll.kvaDbAddAttributeDefinition(self._handle, ct.byref(adh))
        dll.kvaDbSetAttributeDefinitionType(adh, type.value)
        dll.kvaDbSetAttributeDefinitionName(adh, name.encode('utf-8'))
        dll.kvaDbSetAttributeDefinitionOwner(adh, owner)

        atr_def = AttributeDefinition(self, adh, definition)
        return atr_def

    def new_message(self, name, id, flags=0, dlc=None, comment=None):
        """Create a new message in the database.

        Args:
            name (str): name of message
            id (int): message id
            flags (int, optional): message flags, e.g. `kvadblib.MessageFlag.EXT`

        Returns:
            `~canlib.kvadblib.message.Message`

        """
        mh = ct.c_void_p(None)
        dll.kvaDbAddMsg(self._handle, ct.byref(mh))
        try:
            message = Message(self, mh, name, id, flags, dlc, comment)
        except KvdOnlyOneAllowed:
            # If KvdOnlyOneAllowed is thrown, the message was created but not
            # named properly, in which case we need to delete the message
            # before calling the users attention
            dll.kvaDbDeleteMsg(self._handle, mh)
            raise
        return message

    def new_node(self, name, comment=None):
        """Create a new node in the database.

        Args:
            name (str): name of message
            comment (str, optional): message comment

        Returns:
            `Node`

        """
        nh = ct.c_void_p(None)
        dll.kvaDbAddNode(self._handle, ct.byref(nh))
        try:
            node = Node(self, nh, name, comment)
        except KvdOnlyOneAllowed:
            # If KvdOnlyOneAllowed is thrown, the node was created but not
            # named properly, in which case we need to delete the node
            # before calling the users attention
            dll.kvaDbDeleteNode(self._handle, nh)
            raise
        return node

    def node_in_signal(self, node, signal):
        """Check if signal has been added to node.

        Returns:
            True:  signals contains node
            False: otherwise
        """
        try:
            dll.kvaDbSignalContainsReceiveNode(signal._handle, node._handle)
        except KvdNoNode:
            return False
        return True

    def nodes(self):
        """Return a generator containing all database nodes."""
        nh = ct.c_void_p(None)
        try:
            dll.kvaDbGetFirstNode(self._handle, ct.byref(nh))
        except KvdNoNode:
            return
        while nh.value is not None:
            yield Node(self, nh)
            nh = ct.c_void_p()
            try:
                dll.kvaDbGetNextNode(self._handle, ct.byref(nh))
            except KvdNoNode:
                return

    def set_attribute_value(self, name, value):
        """Set value of attribute *name* on database.

        If no attribute called *name* is set on database, attach a database
        attribute from the database attribute definition first.

        .. versionadded:: 1.6

        """
        ah = ct.c_void_p()

        # Try and find attribute on database
        try:
            dll.kvaDbGetAttributeByName(self._handle, name.encode('utf-8'), ct.byref(ah))
        except KvdNoAttribute:
            # If no attribute was found, lookup the attribute definition and
            # add a new attribute to the message
            attrib_def = self.get_attribute_definition_by_name(name)
            dll.kvaDbAddAttribute(self._handle, attrib_def._handle, ct.byref(ah))
        # Set the value in the message attribute
        attribute = Attribute(self, ah)
        attribute.value = value

    def write_file(self, filename):
        """Write a database to file.

        Args:
            filename (str): file to write database to

        """
        dll.kvaDbWriteFile(self._handle, filename.encode('utf-8'))

    @property
    def flags(self):
        """Get the database flags.

        E.g. DATABASE_FLAG_J1939
        """
        flags = ct.c_uint()
        dll.kvaDbGetFlags(self._handle, ct.byref(flags))
        return flags.value

    @flags.setter
    def flags(self, value):
        """Set the database flags.

        E.g. DATABASE_FLAG_J1939
        """
        dll.kvaDbSetFlags(self._handle, value)

    @property
    def name(self):
        """`str`: The current database name (read-only)"""
        buf = ct.create_string_buffer(255)
        dll.kvaDbGetDatabaseName(self._handle, buf, ct.sizeof(buf))
        return buf.value.decode('utf-8')

    @property
    def protocol(self):
        """`ProtocolType`: The database protocol"""
        p = ct.c_int()
        dll.kvaDbGetProtocol(self._handle, ct.byref(p))
        return ProtocolType(p.value)

    @protocol.setter
    def protocol(self, value):
        dll.kvaDbSetProtocol(self._handle, value)
