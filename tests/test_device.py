import pytest
from kvprobe import features

from canlib.device import Device, connected_devices
from canlib.ean import EAN


def test_find(channel_no):
    dev = Device.find(channel_number=channel_no)
    assert dev.channel_number() == channel_no
    ean = dev.ean
    serial = dev.serial
    assert dev.isconnected()

    assert Device.find(ean=ean) == dev
    assert Device.find(serial=serial) == dev

    dev2 = Device(ean=dev.ean, serial=dev.serial)
    assert dev2 == dev
    assert dev2.channel_number() == channel_no


def test_can_dev(channel_no):
    dev = Device.find(channel_number=channel_no)
    with dev.open_channel() as ch:
        print(ch)
    print(dev.channel_data())
    ioc = dev.iocontrol()
    print(ioc)
    ioc.channel.close()


def test_device_issubset():
    d_890_2 = Device(ean=EAN('67890-1'), serial=2)
    d_890_1 = Device(ean=EAN('67890-1'), serial=1)
    d_891_2 = Device(ean=EAN('00891-2'), serial=2)
    d_890_x = Device(ean=EAN('67890-1'), serial=None)
    d_891_x = Device(ean=EAN('67891-2'), serial=None)
    d_xxx_2 = Device(ean=None, serial=2)
    d_xxx_1 = Device(ean=None, serial=1)
    d_xxx_x = Device(ean=None, serial=None)
    assert not d_890_2.issubset(d_890_1)
    assert not d_890_2.issubset(d_891_2)
    assert d_890_2.issubset(d_890_x)
    assert not d_890_2.issubset(d_891_x)
    assert d_890_2.issubset(d_xxx_2)
    assert not d_890_2.issubset(d_xxx_1)
    assert d_890_2.issubset(d_xxx_x)

    assert d_xxx_1.issubset(d_xxx_1)
    assert not d_xxx_1.issubset(d_xxx_2)
    assert not d_xxx_1.issubset(d_890_1)
    assert not d_xxx_1.issubset(d_891_x)


@pytest.mark.feature(features.logger_v2)
def test_memo_dev(channel_no):
    dev = Device.find(channel_number=channel_no)
    with dev.memorator() as memo:
        print(memo)


def test_lin_dev(lin_no):
    dev = Device.find(channel_number=lin_no)
    with dev.lin_master() as ch:
        print(ch)
    with dev.lin_slave() as ch:
        print(ch)


def test_connected_devices():
    for dev in connected_devices():
        print(dev)


def test_unconnected():
    dev = Device(ean=EAN('67890-1'), serial=-1)
    print(dev.probe_info())

    assert dev.isconnected() is False


def test_remote(local_r_no):
    dev = Device.find(channel_number=local_r_no)
    print(dev.remote())
