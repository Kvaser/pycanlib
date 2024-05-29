import os
import random
from collections import OrderedDict, namedtuple

import pytest

from canlib import CanlibException, Frame, canlib, kvadblib

DummyMessage = namedtuple('DummyMessage', 'name id flags dlc comment')


DummySignal = namedtuple(
    'DummySignal', 'name type byte_order mode size scaling ' 'limits unit comment'
)


DummyNode = namedtuple('DummyNode', 'name comment')


MLDA = DummyMessage(name='TempMessage01', id=340, flags=0, dlc=4, comment='Rev message 01.')
MLDB = DummyMessage(
    name='TempMessage02', id=341, flags=kvadblib.MessageFlag.EXT, dlc=6, comment='Rev message 02.'
)
MLDC = DummyMessage(name='TempMessage03', id=342, flags=0, dlc=8, comment='Temp message 03.')

MLDD = DummyMessage(name='TempMessage04', id=0xC99FEFE, flags=kvadblib.MessageFlag.EXT | kvadblib.MessageFlag.J1939, dlc=8, comment='J1939 message.')


SLDA = DummySignal(
    name='S01',
    type=kvadblib.SignalType.UNSIGNED,
    byte_order=kvadblib.SignalByteOrder.INTEL,
    mode=kvadblib.SignalMultiplexMode.MUX_INDEPENDENT,
    size=kvadblib.ValueSize(startbit=0, length=32),
    scaling=kvadblib.ValueScaling(factor=0.02, offset=10),
    limits=kvadblib.ValueLimits(min=-100, max=1000),
    unit='C',
    comment='The first temperature signal.',
)

SLDB = DummySignal(
    name='S02',
    type=kvadblib.SignalType.SIGNED,
    byte_order=kvadblib.SignalByteOrder.INTEL,
    mode=kvadblib.SignalMultiplexMode.MUX_INDEPENDENT,
    size=kvadblib.ValueSize(startbit=32, length=8),
    scaling=kvadblib.ValueScaling(factor=0.01, offset=-10),
    limits=kvadblib.ValueLimits(min=0, max=100),
    unit='C',
    comment='The second temperature signal.',
)

SLDC = DummySignal(
    name='S03',
    type=kvadblib.SignalType.UNSIGNED.value,
    byte_order=kvadblib.SignalByteOrder.INTEL.value,
    mode=kvadblib.SignalMultiplexMode.SIGNAL.value,
    size=kvadblib.ValueSize(startbit=41, length=16),
    scaling=kvadblib.ValueScaling(factor=0.01, offset=1),
    limits=kvadblib.ValueLimits(min=0, max=400),
    unit='K',
    comment='The third temperature signal.',
)

SLDD = DummySignal(
    name='S04',
    type=kvadblib.SignalType.FLOAT.value,
    byte_order=kvadblib.SignalByteOrder.INTEL.value,
    mode=kvadblib.SignalMultiplexMode.SIGNAL.value,
    size=kvadblib.ValueSize(startbit=41, length=16),
    scaling=kvadblib.ValueScaling(factor=0.01, offset=1),
    limits=kvadblib.ValueLimits(min=0, max=400),
    unit='F',
    comment='The fourth (floating) temperature signal.',
)

SLDE = DummySignal(
    name='S05',
    type=kvadblib.SignalType.UNSIGNED.value,
    byte_order=kvadblib.SignalByteOrder.INTEL.value,
    mode=kvadblib.SignalMultiplexMode.SIGNAL.value,
    size=kvadblib.ValueSize(startbit=0, length=4),
    scaling=kvadblib.ValueScaling(factor=1, offset=0),
    limits=kvadblib.ValueLimits(min=0, max=400),
    unit='F',
    comment='The fourth (floating) temperature signal.',
)

SLDF = DummySignal(
    name='S06',
    type=kvadblib.SignalType.ENUM_UNSIGNED.value,
    byte_order=kvadblib.SignalByteOrder.INTEL.value,
    mode=kvadblib.SignalMultiplexMode.SIGNAL.value,
    size=kvadblib.ValueSize(startbit=0, length=8),
    scaling=kvadblib.ValueScaling(factor=1, offset=0),
    limits=kvadblib.ValueLimits(min=0, max=0),
    unit='enums',
    comment='The fifth (enum) signal.',
)


NLDA = DummyNode(name='N01', comment='The first node.')
NLDB = DummyNode(name='N02', comment='A second node.')
NLDC = DummyNode(name='N03', comment='The laste of the nodes.')

ALDA = kvadblib.MinMaxDefinition(default=6, min=0, max=100)
ALDB = kvadblib.MinMaxDefinition(default=5.1, min=1.0, max=10.1)
ALDC = kvadblib.DefaultDefinition(default='My_default_string')


def test_bytes_dlc_conversion():
    bytes = 0
    dlc = kvadblib.bytes_to_dlc(bytes, kvadblib.ProtocolType.CAN)
    assert dlc == 0
    bytes = kvadblib.dlc_to_bytes(dlc, kvadblib.ProtocolType.CAN)
    assert bytes == 0

    bytes = 1
    dlc = kvadblib.bytes_to_dlc(bytes, kvadblib.ProtocolType.CAN)
    assert dlc == 1
    bytes = kvadblib.dlc_to_bytes(dlc, kvadblib.ProtocolType.CAN)
    assert bytes == 1

    bytes = 8
    dlc = kvadblib.bytes_to_dlc(bytes, kvadblib.ProtocolType.CAN)
    assert dlc == 8
    bytes = kvadblib.dlc_to_bytes(dlc, kvadblib.ProtocolType.CAN)
    assert bytes == 8

    bytes = 9
    with pytest.raises(kvadblib.KvdErrInParameter):
        dlc = kvadblib.bytes_to_dlc(bytes, kvadblib.ProtocolType.CAN)

    dlc = 10
    bytes = kvadblib.dlc_to_bytes(dlc, kvadblib.ProtocolType.CAN)
    assert bytes == 8

    bytes = 0
    dlc = kvadblib.bytes_to_dlc(bytes, kvadblib.ProtocolType.CANFD)
    assert dlc == 0
    bytes = kvadblib.dlc_to_bytes(dlc, kvadblib.ProtocolType.CANFD)
    assert bytes == 0

    bytes = 15
    with pytest.raises(kvadblib.KvdErrInParameter):
        dlc = kvadblib.bytes_to_dlc(bytes, kvadblib.ProtocolType.CANFD)

    bytes = 24
    dlc = kvadblib.bytes_to_dlc(bytes, kvadblib.ProtocolType.CANFD)
    assert dlc == 12
    bytes = kvadblib.dlc_to_bytes(dlc, kvadblib.ProtocolType.CANFD)
    assert bytes == 24

    bytes = 64
    dlc = kvadblib.bytes_to_dlc(bytes, kvadblib.ProtocolType.CANFD)
    assert dlc == 15
    bytes = kvadblib.dlc_to_bytes(dlc, kvadblib.ProtocolType.CANFD)
    assert bytes == 64


def test_create_db_rename_and_open(tmpdir):
    db = kvadblib.Dbc(name='Test-Db-0')
    file_name = str(tmpdir / 'db_empty.dbc')
    db.write_file(file_name)
    db.close()

    dst_name = str(tmpdir / 'db_empty_new_name.dbc')
    os.rename(file_name, dst_name)

    db = kvadblib.Dbc(filename=dst_name)
    assert db.name == 'db_empty_new_name'


def test_create_db(tmpdir):
    """Create empty database, close and open again."""
    with pytest.raises(TypeError) as excinfo:
        db = kvadblib.Dbc()
    assert "Either a name or filename must to be given." in str(excinfo.value)

    db = kvadblib.Dbc(name='Test-Db-1')
    assert db.name == 'Test-Db-1'

    db.write_file(str(tmpdir / 'db_create.dbc'))
    assert db.name == 'Test-Db-1'
    db.close()

    db = kvadblib.Dbc(name='Test-Db-2')
    assert db.name == 'Test-Db-2'

    db.write_file(str(tmpdir / 'db_add.dbc'))
    db.close()


def test_create_db_attributes(tmpdir):
    db = kvadblib.Dbc(name='Test-Db-3')

    # Missing attributes raise an error
    with pytest.raises(AttributeError):
        print(db.missing_attribute)
    # Setting missing attributes does not raise an error
    # with pytest.raises(AttributeError):
    db.missing_attribute = 'NonExisting'

    # kvaDbSetFlags() is currently not enabled
    db.flags = kvadblib.DATABASE_FLAG_J1939
    assert db.flags == 0  # kvadblib.DATABASE_FLAG_J1939

    # verify setting protocol
    db.protocol = kvadblib.ProtocolType.LIN
    assert db.protocol == kvadblib.ProtocolType.LIN

    # verify reading protocol_properties
    protocol_properties = kvadblib.get_protocol_properties(kvadblib.ProtocolType.CAN)
    assert protocol_properties.maxMessageDlc == 15
    assert protocol_properties.maxSignalLength == 32

    protocol_properties = kvadblib.get_protocol_properties(kvadblib.ProtocolType.CANFD)
    assert protocol_properties.maxMessageDlc == 15
    assert protocol_properties.maxSignalLength == 64

    file_name = str(tmpdir / 'db_attributes.dbc')

    db.write_file(file_name)
    db.close()

    db = kvadblib.Dbc(filename=file_name)

    # kvaDbSetFlags() "is currently not enabled" in API
    assert db.flags == 0  # kvadblib.DATABASE_FLAG_J1939
    assert db.protocol == kvadblib.ProtocolType.LIN
    db.close()


def test_db_attribute_definition(tmpdir):
    db = kvadblib.Dbc(name='Test-delete-attr-definition')

    with pytest.raises(kvadblib.KvdNoAttribute):
        db.delete_attribute_definition('unknown_ad_name')

    # A clean database still has the 'BusType' attribute definition
    assert len(list(db.attribute_definitions())) == 1

    # Trying to delete a used attribute definition should fail
    with pytest.raises(kvadblib.KvdInUse):
        db.delete_attribute_definition('BusType')

    db.delete_attribute('BusType')
    db.delete_attribute_definition('BusType')

    assert len(list(db.attribute_definitions())) == 0
    for attribute in db.attributes():
        print(attribute)
        assert 0, "There should be no attributes in database."

    with pytest.raises(kvadblib.KvdNoAttribute):
        db.get_attribute_value('BusType')

    db.new_attribute_definition(
        name='my_int_msg_attrib',
        owner=kvadblib.AttributeOwner.DB,
        type=kvadblib.AttributeType.INTEGER,
        definition=ALDA,
    )
    assert len(list(db.attribute_definitions())) == 1

    db.get_attribute_definition_by_name('my_int_msg_attrib')
    db.delete_attribute_definition('my_int_msg_attrib')
    with pytest.raises(kvadblib.KvdNoAttribute):
        db.delete_attribute_definition('unknown_ad_name')
    assert len(list(db.attribute_definitions())) == 0

    filename = str(tmpdir / db.name + '.dbc')
    db.write_file(filename)

    db.close()


def test_create_db_messages(tmpdir):
    db = kvadblib.Dbc(name='Test-Db-3')

    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )

    with pytest.raises(kvadblib.KvdOnlyOneAllowed):
        message = db.new_message(MLDA.name, id=123, flags=kvadblib.MessageFlag.EXT)
        # qqqlm cannot create 2 messages with same name

    message = db.get_message_by_name(MLDA.name)
    assert message != MLDB
    # Verify that our __eq__ is ok
    assert message == MLDA
    message.id = 661
    message.flags = 0
    assert message != MLDA
    message.id = MLDA.id
    message.flags = MLDA.flags
    message.dlc = 13
    assert message != MLDA
    message.dlc = MLDA.dlc
    message.comment = "Some random comment"
    assert message != MLDA
    message.comment = MLDA.comment
    assert message == MLDA

    message = db.new_message(name='Unknown', id=666, flags=0, dlc=1)
    message.name = MLDB.name
    message.id = MLDB.id
    message.flags = MLDB.flags
    message.dlc = MLDB.dlc
    message.comment = MLDB.comment
    assert message == MLDB

    message = db.new_message(name=MLDC.name, id=MLDC.id, flags=MLDC.flags)
    message.name = MLDC.name
    message.dlc = MLDC.dlc
    message.comment = MLDC.comment
    assert message == MLDC

    with pytest.raises(kvadblib.KvdNoMessage) as excinfo:
        message = db.get_message_by_id(666, 0)
    assert "No message was found" in str(excinfo.value)

    # We can't find new messages here since we haven't written the database yet...
    # message = db.get_message_by_id(MLDA.id)
    # assert message == MLDA

    name = message.qualified_name
    assert name == f'{db.name}.{message.name}'

    filename = str(tmpdir / 'db_messages.dbc')
    db.write_file(filename)
    db.close()

    rdb = kvadblib.Dbc(filename=filename)
    with pytest.raises(kvadblib.KvdNoMessage):
        message = rdb.get_message_by_id(777, 0)
    with pytest.raises(kvadblib.KvdNoMessage):
        message = rdb.get_message_by_name(name='unknown_name')
    message = rdb.get_message_by_id(MLDA.id, MLDA.flags)
    assert message == MLDA
    message = rdb.get_message_by_name(MLDB.name)
    assert message == MLDB
    message = rdb.get_message_by_id(MLDC.id, MLDC.flags)
    assert message == MLDC
    message = rdb.get_message(id=MLDC.id)
    assert message == MLDC
    message = rdb.get_message(name=MLDA.name)
    assert message == MLDA
    with pytest.raises(kvadblib.KvdNoMessage) as excinfo:
        message = rdb.get_message(id=MLDC.id, name=MLDB.name)
    message = rdb.get_message(id=MLDB.id | MLDB.flags, name=MLDB.name)
    assert message == MLDB

    print(rdb)
    for message in rdb:
        print(f'  Message name: {message.name}')
        print(" " * 4, message)
        assert len(list(message)) == 0
    rdb.close()


def test_db_repr():
    db = kvadblib.Dbc(name='Test-Db-4', protocol=kvadblib.ProtocolType.CANFD)
    assert str(db) == "Dbc Test-Db-4: flags:0, protocol:CANFD, messages:0"

    atr_def = db.new_attribute_definition(
        name='default_attribute',
        owner=kvadblib.AttributeOwner.MESSAGE,
        type=kvadblib.AttributeType.INTEGER,
        definition=kvadblib.MinMaxDefinition(default=6, min=0, max=100),
    )
    print(repr(atr_def))

    message = db.new_message(name='default_message', id=33)
    print(message)

    signal = message.new_signal(name='default_signal')
    print(signal)


def test_create_db_signals(tmpdir):
    db = kvadblib.Dbc(name='Test-Db-4')
    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )

    signal = message.new_signal(**SLDA._asdict())
    assert signal == SLDA

    s2 = message.new_signal(**SLDA._asdict())
    s2.type = kvadblib.SignalType.SIGNED
    assert signal != s2
    s2.type = signal.type
    s2.byte_order = kvadblib.SignalByteOrder.MOTOROLA
    assert signal != s2
    s2.byte_order = signal.byte_order
    s2.mode = kvadblib.SignalMultiplexMode.SIGNAL
    assert signal != s2
    s2.mode = signal.mode
    s2.size = kvadblib.ValueSize(startbit=1, length=32)
    assert signal != s2
    s2.size = signal.size
    s2.scaling = kvadblib.ValueScaling(factor=0.02, offset=1)
    assert signal != s2
    s2.scaling = signal.scaling
    s2.limits = kvadblib.ValueLimits(min=0, max=1)
    assert signal != s2
    s2.limits = signal.limits
    s2.unit = "APK"
    assert signal != s2
    s2.unit = signal.unit
    s2.comment = "Unknown comment"
    assert signal != s2

    sldx = SLDB._replace(name='Unknown signal')  # Make a copy with different name
    signal = message.new_signal(**sldx._asdict())
    assert signal != SLDB
    signal.comment = SLDB.comment
    signal.name = SLDB.name
    assert signal == SLDB

    signal = message.new_signal(**SLDC._asdict())
    assert signal == SLDC

    signal = message.new_signal(**SLDD._asdict())

    name = signal.qualified_name
    assert name == f'{db.name}.{message.name}.{signal.name}'

    signal = message.get_signal(name=SLDA.name)
    assert signal == SLDA
    assert signal.name == SLDA.name
    assert signal.type == SLDA.type
    assert signal.byte_order == SLDA.byte_order
    assert signal.mode == SLDA.mode
    assert signal.size == SLDA.size
    assert signal.scaling == SLDA.scaling
    assert signal.limits == SLDA.limits
    assert signal.unit == SLDA.unit
    assert signal.comment == SLDA.comment

    filename = str(tmpdir / 'db_signals.dbc')
    db.write_file(filename)
    db.close()

    with kvadblib.Dbc(filename=filename) as rdb:
        print("\n", rdb)
        for message in rdb:
            print(f'  {message.name}')
            for signal in message:
                print(f'    {signal.name}')
        print("\n", rdb)
        for message in rdb.messages():
            print(f'  {message.name}')
            for signal in message.signals():
                print(f'    {signal.name}')


def test_db_message():
    db = kvadblib.Dbc(name='Test-Db-message')
    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )

    with pytest.raises(kvadblib.KvdOnlyOneAllowed):
        db.new_message(
            name=MLDA.name, id=666, flags=MLDA.flags, dlc=MLDA.dlc, comment='duplicate message'
        )

    print("\n Messages so far:")
    for message in db.messages():
        print("   ", message)


def test_db_signal():
    db = kvadblib.Dbc(name='Test-Db-5')
    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )

    signal = message.new_signal(**SLDA._asdict())
    assert len(list(message)) == 1
    message.delete_signal(signal)
    assert len(list(message)) == 0


def test_db_node():
    db = kvadblib.Dbc(name='Test-Db-5')
    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )

    signal = message.new_signal(**SLDA._asdict())

    with pytest.raises(kvadblib.KvdNoNode):
        node = db.get_node_by_name('unknown_node')

    node = db.new_node(name=NLDA.name, comment=NLDA.comment)
    assert node == NLDA
    node.comment = 'Another comment'
    assert str(node) == f"Node(name='{NLDA.name}, comment=Another comment')"

    print("\n Nodes so far:")
    for node in db.nodes():
        print("   ", node)

    with pytest.raises(kvadblib.KvdOnlyOneAllowed):
        node = db.new_node(name=NLDA.name, comment='Duplicate node name')

    node = db.new_node(name='secondGo', comment=NLDB.comment)
    assert node != NLDB
    node.name = NLDB.name
    assert node == NLDB

    with pytest.raises(kvadblib.KvdNoNode):
        node = db.get_node_by_name('secondGo')

    node = db.new_node(name=NLDC.name, comment='No comment')
    assert node != NLDC
    node.comment = NLDC.comment
    assert node == NLDC
    assert len(list(db.nodes())) == 3
    print("\n More nodes so far:")
    for node in db.nodes():
        print("   ", node)

    node = db.get_node_by_name(NLDB.name)
    db.delete_node(node)
    assert len(list(db.nodes())) == 2
    with pytest.raises(kvadblib.KvdNoNode):
        node = db.get_node_by_name(NLDB.name)

    # attach node to message
    node = db.get_node_by_name(NLDC.name)
    message.send_node = node
    assert message.send_node == node

    # attach receive node to signal
    assert len(list(signal.nodes())) == 0
    node = db.get_node_by_name(NLDA.name)
    signal.add_node(node)
    assert len(list(signal.nodes())) == 1
    node = db.get_node_by_name(NLDC.name)
    signal.add_node(node)
    assert len(list(signal.nodes())) == 2
    print("\n Receive nodes so far:")
    for node in db.nodes():
        if db.node_in_signal(node, signal):
            print("   ", node)
    print("\n Receive nodes so far too")
    for node in signal.nodes():
        print("   ", node)
    node = db.get_node_by_name(NLDA.name)
    signal.remove_node(node)
    assert len(list(signal.nodes())) == 1


def verify_db_attribute_number_param(owner, atr_def, definition, no_attributes=0):
    # undefined attribute definition should not be found
    with pytest.raises(kvadblib.KvdNoAttribute):
        owner.set_attribute_value(name='attrib_not_found', value=27)
    with pytest.raises(kvadblib.KvdNoAttribute):
        owner.get_attribute_value('attrib_not_found')

    for atr in list(owner.attributes()):
        print('+++', atr)

    print(repr(owner))
    assert len(list(owner.attributes())) == no_attributes

    # Retreive an attribute value, if the owner does not have the attribute,
    # the atribute definition default value should be returned
    # We use pytest.approx to compensate for deviation in floats
    assert owner.get_attribute_value(atr_def.name) == pytest.approx(definition.default)

    # Generate some unique random numbers
    values = random.sample(range(10, 100), 3)

    # Setting an owner attribute definition should work
    owner.set_attribute_value(name=atr_def.name, value=values[0])
    assert owner.get_attribute_value(name=atr_def.name) == values[0]

    # one more attribute definition should now have been set
    assert len(list(owner.attributes())) == no_attributes + 1
    assert list(owner.attributes())[-1].name == atr_def.name

    # set new attribute value
    owner.set_attribute_value(name=atr_def.name, value=values[1])
    assert owner.get_attribute_value(name=atr_def.name) == values[1]

    # Deleting an attribute should work
    owner.delete_attribute(name=atr_def.name)
    assert owner.get_attribute_value(name=atr_def.name) != values[1]
    assert owner.get_attribute_value(name=atr_def.name) != values[0]

    # original number of attributes should be left
    assert len(list(owner.attributes())) == no_attributes

    # Rename an attribute definition
    name = 'new_' + atr_def.name
    atr_def.name = name
    with pytest.raises(kvadblib.KvdNoAttribute):
        owner.delete_attribute(name=name)
    owner.set_attribute_value(name=name, value=values[2])
    assert owner.get_attribute_value(name=name) == values[2]


@pytest.mark.parametrize("attribute_type", [kvadblib.AttributeType.INTEGER, kvadblib.AttributeType.HEX])
def test_db_attribute_integer_param(tmpdir, attribute_type):
    db_name = f'Test-Db-5-{attribute_type.name}'
    db = kvadblib.Dbc(name=db_name)
    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )
    signal = message.new_signal(**SLDA._asdict())

    node = db.new_node(name=NLDA.name, comment=NLDA.comment)

    message_atr_def = db.new_attribute_definition(
        name='my_int_msg_attrib',
        owner=kvadblib.AttributeOwner.SIGNAL,  # going to change it shortly, hence misleading variable name
        type=attribute_type,
        definition=ALDA,
    )

    assert len(list(db.nodes())) == 1
    assert len(list(message.attributes())) == 0

    # It should be possible to set owner
    assert message_atr_def.owner == kvadblib.AttributeOwner.SIGNAL
    message_atr_def.owner = kvadblib.AttributeOwner.MESSAGE
    assert message_atr_def.owner == kvadblib.AttributeOwner.MESSAGE

    signal_atr_def = db.new_attribute_definition(
        name='my_int_sig_attrib',
        owner=kvadblib.AttributeOwner.SIGNAL,
        type=attribute_type,
        definition=ALDA,
    )
    node_atr_def = db.new_attribute_definition(
        name='my_int_node_attrib',
        owner=kvadblib.AttributeOwner.NODE,
        type=attribute_type,
        definition=ALDA,
    )

    db_atr_def = db.new_attribute_definition(
        name='my_int_db_attrib',
        owner=kvadblib.AttributeOwner.DB,
        type=attribute_type,
        definition=ALDA,
    )

    verify_db_attribute_number_param(message, message_atr_def, ALDA)
    verify_db_attribute_number_param(signal, signal_atr_def, ALDA)
    verify_db_attribute_number_param(node, node_atr_def, ALDA)
    # The database has the database attribute 'BusType' set by default
    # so we set no_attributes to 1
    verify_db_attribute_number_param(db, db_atr_def, ALDA, no_attributes=1)

    # verify string attribute
    message_atr_def = db.new_attribute_definition(
        name='my_string_msg_attrib',
        owner=kvadblib.AttributeOwner.MESSAGE,
        type=kvadblib.AttributeType.STRING,
        definition=ALDC,
    )

    # undefined attribute definition should not be found
    with pytest.raises(kvadblib.KvdNoAttribute):
        message.set_attribute_value(name='attrib_not_found', value='Hello')
    with pytest.raises(kvadblib.KvdNoAttribute):
        message.get_attribute_value('attrib_not_found')

    # one (old) attribute definition is set so far
    assert len(list(message.attributes())) == 1

    # Retreive an attribute value, if the owner does not have the attribute,
    # the atribute definition default value should be returned
    assert message.get_attribute_value(message_atr_def.name) == ALDC.default

    db_filename = str(tmpdir / db_name + '.dbc')
    db.write_file(db_filename)
    db.close()


def test_introduce_attribute_type_mismatch():
    db = kvadblib.Dbc(name='Test-Db-5.5')
    message = db.new_message(
        name=MLDA.name,
        id=MLDA.id,
        flags=MLDA.flags,
        dlc=MLDA.dlc,
        comment=MLDA.comment,
    )

    _ = message.new_signal(**SLDA._asdict())
    _ = db.new_node(name=NLDA.name, comment=NLDA.comment)
    _ = db.new_attribute_definition(
        name='my_int_sig_attrib',
        owner=kvadblib.AttributeOwner.SIGNAL,
        type=kvadblib.AttributeType.INTEGER,
        definition=ALDA,
    )

    with pytest.raises(kvadblib.KvdError):
        message.set_attribute_value(name='my_int_sig_attrib', value=5.5)

    db.close()


def test_db_load_bogus_file():
    with pytest.raises(kvadblib.KvdError) as excinfo:
        kvadblib.Dbc(filename="this_file_does_not_exist.dbc")
    assert excinfo.value.status == kvadblib.Error.DB_FILE_OPEN


def test_db_load_incorrect_dbc_file(datadir):
    with pytest.raises(kvadblib.KvdDbFileParse):
        kvadblib.Dbc(filename=os.path.join(datadir, "invalid.dbc"))


def test_db_retrieve_parse_errors(datadir):
    kvadblib.Dbc(filename=os.path.join(datadir, "engine_example.dbc"))
    errmsg1 = kvadblib.get_last_parse_error()
    assert not errmsg1  # not null/empty

    with pytest.raises(kvadblib.KvdDbFileParse):
        kvadblib.Dbc(filename=os.path.join(datadir, "invalid.dbc"))
    errmsg2 = kvadblib.get_last_parse_error()
    assert errmsg2  # null/empty

    kvadblib.Dbc(filename=os.path.join(datadir, "engine_example.dbc"))
    errmsg3 = kvadblib.get_last_parse_error()
    assert not errmsg3  # not null/empty


def test_attribute_enum():
    db = kvadblib.Dbc(name='Test-Db-6')
    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )
    enums = {'0': 0, '1': 1}
    enum_def = kvadblib.EnumDefaultDefinition(default=0, enums=enums)
    atr_def = db.new_attribute_definition(
        name='CANFD_BRS',
        owner=kvadblib.AttributeOwner.MESSAGE,
        type=kvadblib.AttributeType.ENUM,
        definition=enum_def,
    )
    atr_def.add_enum_definition({'2': 2})

    # Verify that we get default value
    assert message.get_attribute_value('CANFD_BRS') == enum_def.default

    message.set_attribute_value('CANFD_BRS', 1)
    atr = message.get_attribute_value('CANFD_BRS')
    assert atr == 1

    message.set_attribute_value('CANFD_BRS', 0)
    atr = message.get_attribute_value('CANFD_BRS')
    assert atr == 0

    adf = db.get_attribute_definition_by_name('CANFD_BRS')
    print(type(adf))
    print(adf.definition.enums)
    assert adf.definition.enums == {'0': 0, '1': 1, '2': 2}

    # FB#23365 Bug kvadblib: enum members must be defined in value order
    atr_def.add_enum_definition(OrderedDict([('4', 4), ('3', 3)]))
    assert {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4} == adf.definition.enums

    db.close()


def test_signal_enum():
    db = kvadblib.Dbc(name='Test-Db-6')
    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )
    enums = {'One': 1, 'Two': 2, 'Three': 3}

    # Verify that we do not need to specify all fields
    signal = message.new_signal(name=SLDF.name, type=SLDF.type, size=SLDF.size, enums=enums)

    # Three enums was defined at creation time
    assert len(signal.enums) == 3
    signal.add_enum_definition({'Many': 4})
    assert len(signal.enums) == 4

    print(signal.enums)
    signal.enums = enums
    assert len(signal.enums) == 3
    assert signal.enums == enums
    signal.enums = {}
    assert len(signal.enums) == 0

    db.close()


def test_signal_enum_mode(tmpdir):
    db_name = 'Test-Db-multiplex_test'
    scaling = kvadblib.ValueScaling(factor=2, offset=-40)
    mode = 2
    with kvadblib.Dbc(name=db_name) as db:
        # Create new message
        message = db.new_message(
            name='M0OUT', id=417529712, flags=kvadblib.MessageFlag.EXT, dlc=8, comment=''
        )
        # Set message attribute
        message_atr_def = db.new_attribute_definition(
            name='GenMsgCycleTime',
            owner=kvadblib.AttributeOwner.MESSAGE,
            type=kvadblib.AttributeType.INTEGER,
            definition=kvadblib.MinMaxDefinition(default=0, min=0, max=65535),
        )
        message.set_attribute_value(message_atr_def.name, 500)
        # Create signal
        signal = message.new_signal(
            name='CDS',
            type=kvadblib.SignalType.ENUM_UNSIGNED,
            byte_order=kvadblib.SignalByteOrder.INTEL,
            mode=2,
            size=kvadblib.ValueSize(startbit=8, length=8),
            scaling=scaling,
            limits=kvadblib.ValueLimits(min=-40, max=160),
            unit='C',
            comment='',
            enums={'error': 254, 'not_available': 255},
        )
        print(signal)
        db_filename = str(tmpdir / db_name + '.dbc')
        db.write_file(db_filename)

    with kvadblib.Dbc(filename=db_filename) as db:
        msg = db.get_message(name='M0OUT')
        sig = msg.get_signal_by_name('CDS')
        print(sig)
        assert sig.mode == mode
        assert sig.scaling == scaling


def test_db_attribute_float_param():
    db = kvadblib.Dbc(name='Test-Db-5')
    message = db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )
    signal = message.new_signal(**SLDA._asdict())
    node = db.new_node(name=NLDA.name, comment=NLDA.comment)

    message_atr_def = db.new_attribute_definition(
        name='my_int_msg_attrib',
        owner=kvadblib.AttributeOwner.MESSAGE,
        type=kvadblib.AttributeType.FLOAT,
        definition=ALDB,
    )
    signal_atr_def = db.new_attribute_definition(
        name='my_int_sig_attrib',
        owner=kvadblib.AttributeOwner.SIGNAL,
        type=kvadblib.AttributeType.FLOAT,
        definition=ALDB,
    )
    node_atr_def = db.new_attribute_definition(
        name='my_int_node_attrib',
        owner=kvadblib.AttributeOwner.NODE,
        type=kvadblib.AttributeType.FLOAT,
        definition=ALDB,
    )

    verify_db_attribute_number_param(message, message_atr_def, ALDB)
    verify_db_attribute_number_param(signal, signal_atr_def, ALDB)
    verify_db_attribute_number_param(node, node_atr_def, ALDB)
    db.close()


def test_db_attribute_integer(tmpdir):
    db = kvadblib.Dbc(name='Test-Db-5')
    db.new_message(
        name=MLDA.name, id=MLDA.id, flags=MLDA.flags, dlc=MLDA.dlc, comment=MLDA.comment
    )

    message = db.new_message(
        name=MLDB.name, id=MLDB.id, flags=MLDB.flags, dlc=MLDB.dlc, comment=MLDB.comment
    )
    signal = message.new_signal(**SLDA._asdict())
    node = db.new_node(name=NLDA.name, comment=NLDA.comment)

    with pytest.raises(kvadblib.KvdOnlyOneAllowed):
        node = db.new_node(name=NLDA.name, comment=NLDA.comment)

    atr_def = db.new_attribute_definition(
        name='my_int_msg_attrib',
        owner=kvadblib.AttributeOwner.MESSAGE,
        type=kvadblib.AttributeType.INTEGER,
        definition=ALDA,
    )

    assert atr_def.definition == ALDA

    for atr_def in db.attribute_definitions():
        print("  ", atr_def)

    atr_def = db.new_attribute_definition(
        name='my_int_sig_attrib',
        owner=kvadblib.AttributeOwner.SIGNAL,
        type=kvadblib.AttributeType.INTEGER,
        definition=ALDA,
    )

    atr_def = db.new_attribute_definition(
        name='my_int_node_attrib',
        owner=kvadblib.AttributeOwner.NODE,
        type=kvadblib.AttributeType.INTEGER,
        definition=ALDA,
    )

    # get and set of attributes with wrong owner should not be accessible
    with pytest.raises(kvadblib.KvdWrongOwner):
        message.set_attribute_value(name='my_int_sig_attrib', value=27)

    with pytest.raises(kvadblib.KvdWrongOwner):
        message.get_attribute_value(name='my_int_sig_attrib')

    with pytest.raises(kvadblib.KvdNoAttribute):
        message.delete_attribute(name='my_int_sig_attrib')

    with pytest.raises(kvadblib.KvdWrongOwner):
        signal.set_attribute_value(name='my_int_node_attrib', value=27)

    with pytest.raises(kvadblib.KvdWrongOwner):
        signal.get_attribute_value(name='my_int_node_attrib')

    with pytest.raises(kvadblib.KvdNoAttribute):
        signal.delete_attribute(name='my_int_node_attrib')

    with pytest.raises(kvadblib.KvdWrongOwner):
        node.set_attribute_value(name='my_int_msg_attrib', value=27)

    with pytest.raises(kvadblib.KvdWrongOwner):
        node.get_attribute_value(name='my_int_msg_attrib')

    with pytest.raises(kvadblib.KvdNoAttribute):
        node.delete_attribute(name='my_int_msg_attrib')

    # Our API does not support ENV attributes, so we skip those
    # owner=kvadblib.AttributeOwner.ENV,

    # closing and reopening should be fine
    filename = str(tmpdir / 'db_attributes_temp_1.dbc')
    db.write_file(filename)
    db.close()
    db = kvadblib.Dbc(filename=filename)
    message = db.get_message(name=MLDB.name)
    assert message == MLDB

    print("Some attributes:\n")
    i = 0
    for definition in db.attribute_definitions():
        print("- ", definition.name)
        i += 1

    assert i == 4
    db.write_file(str(tmpdir / 'db_attributes.dbc'))
    db.close()


def test_empty_db(tmpdir):
    """Try finding message from an empty db."""
    filename = str(tmpdir / 'db_empty.dbc')

    with kvadblib.Dbc(name='Test-Db-6') as db:
        db.write_file(filename)

    with kvadblib.Dbc(filename=filename) as db:
        assert len(list(db.nodes())) == 0
        for _node in db.nodes():
            assert True, "no nodes should be found in database"

        # No messages are defined
        assert len(db) == 0
        for _message in db:
            assert True, "no messages should be found in database"

        # One message is defined
        message = db.new_message(name=MLDA.name, id=MLDA.id)
        assert len(db) == 1
        assert len(message) == 0
        for _signal in db:
            assert True, "no signals should be found in message"

        message.new_signal(name=SLDA.name)
        assert len(message) == 1

        db.write_file(filename)

    with kvadblib.Dbc(filename=filename) as db:
        assert len(db) == 1
        message = db.get_message(name=MLDA.name)
        db.delete_message(message)
        assert len(db) == 0


def test_save_retrieve():
    db = kvadblib.Dbc(name='T-base')

    dintel_sig = DummySignal(
        name='Intel',
        type=kvadblib.SignalType.UNSIGNED,
        byte_order=kvadblib.SignalByteOrder.INTEL,
        mode=kvadblib.SignalMultiplexMode.MUX_INDEPENDENT,
        size=kvadblib.ValueSize(startbit=0, length=32),
        scaling=kvadblib.ValueScaling(factor=0.02, offset=10),
        limits=kvadblib.ValueLimits(min=-100, max=1000),
        unit='g',
        comment='Intel byte order.',
    )

    dmotorola_sig = DummySignal(
        name='Motorola',
        type=kvadblib.SignalType.UNSIGNED,
        byte_order=kvadblib.SignalByteOrder.MOTOROLA,
        mode=kvadblib.SignalMultiplexMode.MUX_INDEPENDENT,
        size=kvadblib.ValueSize(startbit=32, length=16),
        scaling=kvadblib.ValueScaling(factor=0.4, offset=5),
        limits=kvadblib.ValueLimits(min=-10, max=100),
        unit='-',
        comment='Motorola byte order.',
    )

    message = db.new_message(name='MSG', id=340, flags=kvadblib.MessageFlag.EXT)
    print(message)

    intel_sig = message.new_signal(**dintel_sig._asdict())
    print(intel_sig)

    motorola_sig = message.new_signal(**dmotorola_sig._asdict())
    print(motorola_sig)

    rmessage = db.get_message_by_name('MSG')
    print(rmessage)
    assert rmessage == message

    rintel_sig = rmessage.get_signal_by_name('Intel')
    print(rintel_sig)
    assert rintel_sig == intel_sig == dintel_sig

    rmotorola_sig = rmessage.get_signal_by_name('Motorola')
    print(rmotorola_sig)
    assert rmotorola_sig == motorola_sig == dmotorola_sig


def test_sample_create_new_database(tmpdir):
    db = kvadblib.Dbc(name='T-base')

    # Add a new message
    message = db.new_message(name='TempMessage01', id=340, flags=kvadblib.MessageFlag.EXT)
    message.dlc = 8
    message.comment = 'Temperature message 01.'

    # Add a signal to the new message
    signal = message.new_signal(name='Status')
    signal.comment = 'The status signal.'
    signal.unit = '-'
    signal.byte_order = kvadblib.SignalByteOrder.INTEL
    signal.representation = kvadblib.SignalType.UNSIGNED

    signal.limits = kvadblib.ValueLimits(min=0, max=99999)
    signal.size = kvadblib.ValueSize(startbit=0, length=32)

    # Add a second message with two signals to the database
    message = db.new_message(name='TempMessage02', id=345)
    message.dlc = 8
    message.comment = 'Temperature message 02.'

    # Add a signal to the second message
    signal = message.new_signal('T01')
    signal.comment = 'The first temperature signal.'
    signal.unit = 'C'
    # qqqmac MOTOROLA gives start pos 16 in dbeditfd
    # signal.byte_order = kvaDbLib.SignalByteOrder.MOTOROLA
    # http://mist.kvaser.se/FogBugz/default.asp?15667
    signal.type = kvadblib.SignalType.SIGNED
    signal.byte_order = kvadblib.SignalByteOrder.INTEL
    signal.size = kvadblib.ValueSize(startbit=0, length=32)
    signal.scaling = kvadblib.ValueScaling(factor=0.02, offset=10)
    signal.limits = kvadblib.ValueLimits(min=-100, max=1000)

    # Add another signal to the second message
    signal = message.new_signal('T02')
    signal.comment = 'The second temperature signal.'
    signal.unit = 'C'
    signal.byte_order = kvadblib.SignalByteOrder.INTEL
    signal.type = kvadblib.SignalType.SIGNED
    signal.limits = kvadblib.ValueLimits(min=-100, max=1000)
    signal.scaling = kvadblib.ValueScaling(factor=0.01, offset=-10)
    signal.size = kvadblib.ValueSize(startbit=31, length=32)

    # Save the database to file
    db.write_file(str(tmpdir / 'sample.dbc'))
    db.close()


def test_binding(tmpdir):
    db = kvadblib.Dbc(name='test_binding_db')

    # Add a new message
    message = db.new_message(name='TempMessage01', id=340, flags=kvadblib.MessageFlag.EXT)
    message.dlc = 8
    message.comment = 'Temperature message 01.'

    # Add a signal to the new message
    signal = message.new_signal(name='Status')
    signal.comment = 'The status signal.'
    signal.unit = '-'
    signal.byte_order = kvadblib.SignalByteOrder.INTEL
    signal.representation = kvadblib.SignalType.UNSIGNED
    signal.limits = kvadblib.ValueLimits(min=0, max=99999)
    signal.size = kvadblib.ValueSize(startbit=0, length=32)

    # Add a new message, with same id but not extended id
    message2 = db.new_message(name='TempMessage01b', id=340, flags=0)
    message2.dlc = 8
    message2.comment = 'Temperature message 01.'

    # Two ways to get an empty frame matching the signal
    frame = signal.bind().frame
    assert frame == message.bind().Status.frame

    SIG_VAL = 1234

    # Rebind the frame to the signal it came from, and change its value
    signal.bind(frame).phys = SIG_VAL

    # Check the value just added to the frame by rebinding it
    assert message.bind(frame).Status.phys == SIG_VAL
    assert signal.bind(frame).phys == SIG_VAL

    # reload the database so it knows about the new messages
    filename = str(tmpdir / "sample.dbc")
    db.write_file(filename)
    db.close()
    db = kvadblib.Dbc(filename=filename)

    # Check the value by rebinding through the database itself
    assert db.interpret(frame).Status.phys == SIG_VAL

    db.close()


def test_framebox(datadir):
    db = kvadblib.Dbc(filename=os.path.join(datadir, "engine_example.dbc"))
    framebox = kvadblib.FrameBox(db, messages=("EngineData",))

    with pytest.raises(CanlibException):
        bsig = framebox.signal('UNKNOWN')

    bsig = framebox.signal('PetrolLevel')
    bsig.phys = 1
    print(bsig)
    bsig = framebox.signal('EngPower')
    bsig.phys = 1
    print(bsig)

    frames = list(framebox.frames())
    print(frames)
    assert len(frames) == 1
    assert frames[0].data == b'\x00\x00\x00\x01\x00\x00d\x00'


def test_framebox_canflags(datadir):
    frames_in_dbc = {
        "can_ext": Frame(
            id_=0x12,
            flags=canlib.MessageFlag.EXT,
            data=b'\0' * 8,
        ),
        "can_fd_ext": Frame(
            id_=0x2,
            flags=canlib.MessageFlag.FDF | canlib.MessageFlag.EXT,
            data=b'\0' * 64,
        ),
        "can_fd_ext_brs": Frame(
            id_=0x3,
            flags=canlib.MessageFlag.FDF | canlib.MessageFlag.EXT | canlib.MessageFlag.BRS,
            data=b'\0' * 64,
        ),
        "can_fd_std": Frame(
            id_=0x4,
            flags=canlib.MessageFlag.STD | canlib.MessageFlag.FDF,
            data=b'\0' * 64,
        ),
        "can_fd_std_brs": Frame(
            id_=0x1,
            flags=canlib.MessageFlag.STD | canlib.MessageFlag.FDF | canlib.MessageFlag.BRS,
            data=b'\0' * 64,
        ),
        "can_std": Frame(
            id_=0x11,
            flags=canlib.MessageFlag.STD,
            data=b'\0' * 8,
        ),
    }
    db = kvadblib.Dbc(filename=os.path.join(datadir, "pingerfd.dbc"))
    framebox = kvadblib.FrameBox(db, messages=frames_in_dbc.keys())
    frames = list(framebox.frames())
    for frame in frames_in_dbc.values():
        assert frame in frames


def test_version():
    v = kvadblib.dllversion()
    print(v)
    print(v.major, v.minor)


def test_StringAttribute():
    db = kvadblib.Dbc(name='Test-Db-1')

    db.new_attribute_definition(
        name='str_attr',
        owner=kvadblib.AttributeOwner.MESSAGE,
        type=kvadblib.AttributeType.STRING,
        definition=kvadblib.DefaultDefinition(default=""),
    )

    msg = db.new_message(**MLDA._asdict())

    msg.set_attribute_value('str_attr', "test")

    assert msg.get_attribute_value('str_attr') == "test"


def test_EnumSignal():
    db = kvadblib.Dbc(name='test')

    msg = db.new_message(**MLDA._asdict())

    sig = msg.new_signal(
        name='ESig',
        type=kvadblib.SignalType.ENUM_UNSIGNED,
        enums={
            'spam': 0,
            'eggs': 1,
        },
    )
    assert isinstance(sig, kvadblib.EnumSignal)

    assert sig == msg.get_signal_by_name('ESig')


def test_J1939_message_flag():
    db = kvadblib.Dbc(name='Test-J1939-msg-flag-Db')

    _ = db.new_attribute_definition(
        name='ProtocolType',
        owner=kvadblib.AttributeOwner.DB,
        type=kvadblib.AttributeType.STRING,
        definition=kvadblib.DefaultDefinition(default='J1939'),
    )

    enums = {'StandardCAN': 0, 'ExtendedCAN': 1, 'reserved': 2, 'J1939PG': 3}
    enum_def = kvadblib.EnumDefaultDefinition(default=0, enums=enums)
    _ = db.new_attribute_definition(
        name='VFrameFormat',
        owner=kvadblib.AttributeOwner.MESSAGE,
        type=kvadblib.AttributeType.ENUM,
        definition=enum_def,
    )

    # Add CAN std message
    message = db.new_message(
        name=MLDA.name,
        id=MLDA.id,
        flags=MLDA.flags,
        dlc=MLDA.dlc,
        comment=MLDA.comment,
    )

    message = db.get_message_by_name('TempMessage01')
    assert message == MLDA
    assert message.flags == MLDA.flags
    assert message.get_attribute_value('VFrameFormat') == enums["StandardCAN"]

    # Add CAN EXT message
    message = db.new_message(
        name=MLDB.name,
        id=MLDB.id,
        flags=MLDB.flags,
        dlc=MLDB.dlc,
        comment=MLDB.comment,
    )

    message = db.get_message_by_name('TempMessage02')
    assert message == MLDB
    assert message.flags == MLDB.flags
    assert message.get_attribute_value('VFrameFormat') == enums["ExtendedCAN"]

    # Add J1939 message
    message = db.new_message(
        name=MLDD.name,
        id=MLDD.id,
        flags=MLDD.flags,
        dlc=MLDD.dlc,
        comment=MLDD.comment,
    )

    message = db.get_message_by_name('TempMessage04')
    assert message == MLDD
    assert message.flags == MLDD.flags
    assert message.get_attribute_value('VFrameFormat') == enums["J1939PG"]
