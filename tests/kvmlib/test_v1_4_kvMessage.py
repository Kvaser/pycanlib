from conftest import kvdeprecated

from canlib import kvMessage


@kvdeprecated
def test_kvMessage():
    msg1 = kvMessage.kvMessage(id_=5, data=[1, 2, 3, 4])
    print(f"msg1: {msg1}")
    msg2 = kvMessage.kvMessage(id_=5, data=b'\x01\x02\x03\x04')
    print(f"msg2: {msg2}")
    assert msg1 == msg2

    assert tuple(msg1) == (5, bytearray((1, 2, 3, 4)), 4, 0, None)


@kvdeprecated
def test_padding():
    msg = kvMessage.kvMessage(id_=1, data=b'\x01', dlc=3)
    assert msg.data == bytearray((1, 0, 0))
