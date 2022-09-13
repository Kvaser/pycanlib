from collections import namedtuple
from functools import partial

import pytest

from canlib import Frame, kvadblib

SignalDefinition = namedtuple("SignalDefinition", "name, startbit, length")


@pytest.fixture(scope="module")
def signal_db(tmp_path_factory):
    folder = tmp_path_factory.mktemp("bound_signal_db")
    signals, filename = create_db("DbTestPhysSig", folder)
    return signals, filename


def byteiter(byte):
    for i in range(8):
        yield bool((byte >> i) & 0x1)


def bitlist_slice_to_int(bl, offset, length):
    return sum(bl[i] << (i - offset) for i in range(offset, offset + length))


def create_db(name, path):
    """
        Some calculations in order to understand the bit order...

        Given the following signal definition:
            a: start=0, length=2
            b: start=2, length=3
            c: start=5, length=7
            d: start=12, length=6
            e: start=18, length=6

        we can set the following signals to zero:

        a = 0 when Frame(id_=42, data=[0xfc, 0xff, 0xff])

        signals:   e    |   d   |    c    | b  | a
        values :  63    |  63   |   127   | 7  | 0
        binary : 1111_11 11_1111 _1111_111 1_11 00
        hex    :  f     f     f     f    f     c
        data   : 0xfcffff


        b = 0 when Frame(id_=42, data=[0xe2, 0xff, 0xff])

        signals:   e    |   d   |    c    | b  | a
        values :  63    |  63   |   127   | 0  | 3
        binary : 1111_11 11_1111 _1111_111 0_00 11
        hex    :  f     f     f     f    e     2
        data   : 0xe2ffff

        c = 0 when Frame(id_=42, data=[0x1f, 0xf0, 0xff])

        signals:   e    |   d   |    c    | b  | a
        values :  63    |  63   |    0    | 3  | 3
        binary : 1111_11 11_1111 _0000_000 1_11 11
        hex    :  f     f     f     0    1     f

        d = 0 when Frame(id_=42, data=[0xff, 0x0f, 0xfc])

        signals:   e    |   d   |    c    | b  | a
        values :  63    |   0   |   127   | 3  | 3
        binary : 1111_11 00_0000 _1111_111 1_11 11
        hex    :  f     c     0     f    f     f

        d = 16 when Frame(id_=42, data=[0xff, 0x0f, 0xfd])


        If we now have:

        >>> frame = Frame(id_=42, data=[0x12, 0x34, 0x56])

        hex    :   5    6     3     4    1     2
        binary : 0101_01 10_0011 _0100_000 1_00 10
        signals:   e    |   d   |    c    | b  | a
        values :   21      35       32      4    2

    =========

                   '0b100100011010001010110'  # 0x123456
        '0b10011001000100100011010001010110'  # 0x99123456
                          '0b11010001010110'  # 0x3456

    """
    signal_definitions = [
        SignalDefinition(name="a", startbit=0, length=2),
        SignalDefinition(name="b", startbit=2, length=3),
        SignalDefinition(name="c", startbit=5, length=7),
        SignalDefinition(name="d", startbit=12, length=6),
        SignalDefinition(name="e", startbit=18, length=6),
    ]
    db = kvadblib.Dbc(name=name)

    # The signals dictionary will be filled with functions that, given a
    # bitlist view of the data, will return the raw signal value. Since we have
    # set factor=1 and offset=0, the physical value will be indentical to the
    # raw value.
    signals = {}

    message = db.new_message(name="TestMessage01", id=42, dlc=3)
    for definition in signal_definitions:
        signal = message.new_signal(
            name=definition.name,
            size=kvadblib.ValueSize(startbit=definition.startbit, length=definition.length),
        )

        # Using `partial`, create a new function, based on
        # `bitlist_slice_to_int`, that has the keyword arguments `offset` and
        # `length` set according to the current signal definition.
        signals[signal.name] = partial(
            bitlist_slice_to_int, offset=signal.size.startbit, length=signal.size.length
        )

    filename = path / f"{name}.dbc"
    filename_str = str(filename)
    print(f"Writing {filename_str}")
    db.write_file(filename_str)  # SOF-3460 Dbc.write_file() and Dbc() should take pathlib objects
    db.close
    return signals, filename_str


def print_frame(db, frame):
    try:
        bmsg = db.interpret(frame)
    except kvadblib.KvdNoMessage:
        print(f"<<< No message found for frame with id {frame.id} >>>")
        return
    msg = bmsg._message

    print('/', msg.name)
    if msg.comment:
        print('|', f'"{msg.comment}"')
    for bsig in bmsg:
        print('|', bsig.name + ':', bsig.value, bsig.unit)
    print('\\')


def test_phys_exact_dlc_match(signal_db):
    # signals, filename = create_db("DbTestPhysSig", tmp_path)
    signals, filename = signal_db
    db = kvadblib.Dbc(filename=filename)
    frame_fail = Frame(id_=40, data=[0x12, 0x34, 0x56], dlc=3)
    # <<< No message found for frame with id 40 >>>
    print_frame(db, frame_fail)

    data = [0x12, 0x34, 0x56]
    bl = [bit for byte in data for bit in byteiter(byte)]

    frame = Frame(id_=42, data=data)
    print_frame(db, frame)
    bmsg = db.interpret(frame)
    for bsig in bmsg:
        assert bsig.value == signals[bsig.name](bl)


def test_phys_dlc_too_large(signal_db):
    signals, filename = signal_db
    db = kvadblib.Dbc(filename=filename)

    data = [0x12, 0x34, 0x56]
    bl = [bit for byte in data for bit in byteiter(byte)]

    # Add one extra byte
    frame = Frame(id_=42, data=data + [0x99])
    print_frame(db, frame)
    bmsg = db.interpret(frame)
    for bsig in bmsg:
        assert bsig.value == signals[bsig.name](bl)

    # Sanity test, this should fail
    frame = Frame(id_=42, data=[0x99] + data)
    print_frame(db, frame)
    bmsg = db.interpret(frame)
    for bsig in bmsg:
        # This is true for our data, but for random data, some signal values
        # could happen to be correct...
        assert bsig.value != signals[bsig.name](bl)


def test_phys_dlc_too_small(signal_db):
    signals, filename = signal_db
    db = kvadblib.Dbc(filename=filename)

    data = [0x12, 0x34, 0x56]
    bl = [bit for byte in data for bit in byteiter(byte)]

    # Remove last byte
    frame = Frame(id_=42, data=data[0:2])
    bmsg = db.interpret(frame)
    for bsig in bmsg:
        sig_name = bsig.name
        if sig_name in ("a", "b", "c"):
            assert bsig.value == signals[sig_name](bl)
        else:
            with pytest.raises(kvadblib.KvdErrInParameter):
                _ = bsig.value

    # Sanity test, this should fail
    frame = Frame(id_=42, data=[0x99] + data)
    print_frame(db, frame)
    bmsg = db.interpret(frame)
    for bsig in bmsg:
        # This is true for our data, but for random data, some signal values
        # could happen to be correct...
        assert bsig.value != signals[bsig.name](bl)


def test_raw_dlc_too_small(signal_db):
    signals, filename = signal_db
    db = kvadblib.Dbc(filename=filename)

    data = [0x12, 0x34, 0x56]
    bl = [bit for byte in data for bit in byteiter(byte)]

    # Remove last byte
    frame = Frame(id_=42, data=data[0:2])
    bmsg = db.interpret(frame)
    for bsig in bmsg:
        sig_name = bsig.name
        if sig_name in ("a", "b", "c"):
            assert bsig.raw == signals[sig_name](bl)
        else:
            with pytest.raises(kvadblib.KvdErrInParameter):
                _ = bsig.raw
