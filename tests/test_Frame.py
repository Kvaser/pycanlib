from canlib import Frame


def test_equality():
    msg1 = Frame(id_=5, data=[1, 2, 3, 4])
    print(f"msg1: {msg1}")
    msg2 = Frame(id_=5, data=b'\x01\x02\x03\x04')
    print(f"msg2: {msg2}")
    assert msg1 == msg2

    assert tuple(msg1) == (5, bytearray((1, 2, 3, 4)), 4, 0, None)


def test_padding():
    msg = Frame(id_=1, data=b'\x01', dlc=3)
    assert msg.data == bytearray((1, 0, 0))

    msg = Frame(id_=1, data=b'\x01\x02\x03\x04\x05\x06\x07\x08', dlc=12)
    assert msg.data == bytearray((1, 2, 3, 4, 5, 6, 7, 8))
    assert msg.dlc == 12

    msg = Frame(id_=1, data=b'\x01\x02\x03\x04\x05\x06', dlc=8)
    assert tuple(msg) == (1, bytearray((1, 2, 3, 4, 5, 6, 0, 0)), 8, 0, None)

    # example with large dlc. Frame() does not extend the data in this case
    msg = Frame(id_=1, data=b'\x01\x02\x03\x04\x05\x06', dlc=12)
    assert tuple(msg) == (1, bytearray((1, 2, 3, 4, 5, 6)), 12, 0, None)

    msg = Frame(id_=1, data=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b')
    assert tuple(msg) == (1, bytearray((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0)), 12, 0, None)

    msg = Frame(id_=1, data=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d')
    assert tuple(msg) == (
        1,
        bytearray((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 0, 0)),
        16,
        0,
        None,
    )

    msg = Frame(
        id_=1, data=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11'
    )
    assert tuple(msg) == (
        1,
        bytearray((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 0, 0, 0)),
        20,
        0,
        None,
    )

    msg = Frame(
        id_=1,
        data=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15',
    )
    assert tuple(msg) == (
        1,
        bytearray(
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 0, 0, 0)
        ),
        24,
        0,
        None,
    )

    msg = Frame(
        id_=1,
        data=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19',
    )
    assert tuple(msg) == (
        1,
        bytearray(
            (
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            )
        ),
        32,
        0,
        None,
    )

    msg = Frame(
        id_=1,
        data=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21',
    )
    assert tuple(msg) == (
        1,
        bytearray(
            (
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            )
        ),
        48,
        0,
        None,
    )

    msg = Frame(
        id_=1,
        data=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31',
    )
    assert tuple(msg) == (
        1,
        bytearray(
            (
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                41,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
                49,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            )
        ),
        64,
        0,
        None,
    )
