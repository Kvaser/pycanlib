from conftest import kvdeprecated

import canlib.kvDevice as kvDevice


def test_ean2ean_hi():
    ean_hi = kvDevice.kvDevice.ean2ean_hi("73-30130-00671-3")
    assert ean_hi == 0x73301


def test_ean2ean_lo():
    ean_lo = kvDevice.kvDevice.ean2ean_lo("73-30130-00671-3")
    assert ean_lo == 0x30006713


def test_ean_hi_lo2ean():
    ean = kvDevice.kvDevice.ean_hi_lo2ean(0x73301, 0x30006713)
    assert ean == "73-30130-00671-3"


@kvdeprecated
def test_allDevices():
    devices = kvDevice.kvDevice.allDevices()
    print(f"List all {len(devices)} devices...")
    for dev in devices:
        print("\n", dev)
