import pytest

from canlib.ean import EAN, IllegalEAN


def test_equality():
    assert EAN('12345-6') == EAN('12345-6')
    assert EAN('12345-6') != EAN('99999-9')

    assert EAN('01234-6') == EAN('73-30130-01234-6')


def test_edge_cases():
    assert EAN(12) == '00-00000-00001-2'

    with pytest.raises(IllegalEAN):
        print(EAN('12'))
    with pytest.raises(IllegalEAN):
        print(EAN('01234-01234-01'))
    with pytest.raises(IllegalEAN):
        print(EAN('01-01234-01234-01'))
    with pytest.raises(IllegalEAN):
        print(EAN('01-01234.01234-0'))
    with pytest.raises(IllegalEAN):
        print(EAN('01-0123-401234-0'))
    with pytest.raises(IllegalEAN):
        print(EAN(90101234012340))
    with pytest.raises(IllegalEAN):
        print(EAN([9, 0, 1, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0]))
    with pytest.raises(IllegalEAN):
        print(EAN([0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0]))
    with pytest.raises(IllegalEAN):
        print(EAN(['0', '1', '0', '1', '2', '3', '4', '0', '1', '2', '3', '4', '0']))


def test_creation():
    class source:
        s = '73-30130-01234-5'
        s_short = '01234-5'
        bcd = b'\x45\x23\x01\x30\x01\x33\x07'
        hilo = (0x73301, 0x30012345)
        i = 7330130012345

    s = EAN(source.s)
    s_short = EAN(source.s_short)
    bcd = EAN.from_bcd(source.bcd)
    hilo = EAN.from_hilo(source.hilo)
    i = EAN(source.i)

    assert s == source.s

    assert s == s_short
    assert s == bcd
    assert s == hilo
    assert s == i

    assert str(s) == source.s
    assert s.product() == source.s_short
    assert s.bcd() == source.bcd
    assert s.hilo() == source.hilo
    assert int(s) == source.i
