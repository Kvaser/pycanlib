import sys
import time

import pytest
from conftest import kvdeprecated, winonly

"""Run using pytest, e.g. pytest --cov --cov-report html"""

if sys.platform.startswith('win'):
    from canlib import kvrlib
else:
    kvrlib = NotImplemented


@kvdeprecated
@winonly
def test_import_kvrlib():
    rl = kvrlib.kvrlib()
    version = rl.getVersion()
    print(f"Python kvrlib version: {version}")
    # assert str(version) == "8.23"


@kvdeprecated
@winonly
def test_ean2ean_hi():
    # qqqmac should this be moved one step up?
    ean_hi = kvrlib.kvrlib.ean2ean_hi("73-30130-00671-3")
    # ean_hi = kvrlib.ean2ean_hi("73-30130-00671-3")
    assert ean_hi == 0x73301


@kvdeprecated
@winonly
def test_ean2ean_lo():
    # qqqmac should this be moved one step up?
    ean_lo = kvrlib.kvrlib.ean2ean_lo("73-30130-00671-3")
    assert ean_lo == 0x30006713


@kvdeprecated
@winonly
def test_ean_hi_lo2ean():
    # qqqmac should this be moved one step up?
    ean = kvrlib.kvrlib.ean_hi_lo2ean(0x73301, 0x30006713)
    assert ean == "73-30130-00671-3"


@kvdeprecated
@winonly
def test_address_string():
    from canlib import kvrlib

    rl = kvrlib.kvrlib()
    addr = rl.addressFromString(kvrlib.kvrAddress.Type_IPV4_PORT, "192.168.1.1:8080")
    # qqqmac fails...
    # assert str(addr) == "192.168.1.1:8080 (IPV4_PORT)"
    assert rl.stringFromAddress(addr) == "192.168.1.1:8080"
    addr = rl.addressFromString(kvrlib.kvrAddress.Type_IPV4, "192.168.10.1")
    print(addr)
    assert str(addr) == "192.168.10.1 (IPV4)"
    assert rl.stringFromAddress(addr) == "192.168.10.1"


@kvdeprecated
@winonly
def test_qqqmac():
    from canlib import kvrlib

    rl = kvrlib.kvrlib()
    # qqqmac Remote device needs to be connected
    channel = 5
    try:
        num_profiles = rl.configNoProfilesGet(channel=channel)
    except Exception:
        print("Remote device needs to be connected")
    else:
        assert num_profiles == 4
        active_profile = rl.configActiveProfileGet(channel=channel)
        assert active_profile == 0
        rl.configActiveProfileSet(channel=channel, profile_number=active_profile)
        active_profile = rl.configActiveProfileGet(channel=channel)
        assert active_profile == 0


@winonly
@kvdeprecated
def test_kvrConfig():
    with pytest.raises(kvrlib.KvrError):
        kvrlib.kvrConfig(kvrlib.kvrlib(), password="Bulle")


@pytest.mark.skip(reason="test needs a device on network")
@winonly
@kvdeprecated
def test_discovery_scan():
    print("Scanning for devices")
    addressList = kvrlib.kvrDiscovery.getDefaultAddresses(kvrlib.kvrAddressTypeFlag_BROADCAST)
    print(f"IP addresses to scan for devices on: {addressList}")

    rl = kvrlib.kvrlib()
    discovery = rl.discoveryOpen()
    discovery.setAddresses(addressList)

    print("Scanning devices...\n")
    deviceInfos = discovery.getResults()
    # We should get at least one hit
    assert len(deviceInfos) > 0
    print(f"Scanning result:{deviceInfos}\n")

    discovery.close()
    rl.unload()


@winonly
def test_unknown_error():
    with pytest.raises(kvrlib.KvrError) as excinfo:
        raise kvrlib.exceptions.KvrGeneralError(111)
    assert "Unknown error text (111)" in str(excinfo.value)


@winonly
def test_kvrdeviceinfo():
    import ctypes as ct

    deviceInfo_0 = kvrlib.structures.kvrDeviceInfo()
    deviceInfo_0.ean_hi = ct.c_uint32(1111)
    deviceInfo_0.ean_lo = ct.c_uint32(2222)
    deviceInfo_0.ser_no = ct.c_uint32(3333)
    assert (
        str(deviceInfo_0)
        == """
name/hostname  : '' / ''
  ean/serial   : 457-8ae / 3333
  fw           : v0.0.000
  addr/cli/AP  : - (UNKNOWN) / - (UNKNOWN) / - (UNKNOWN)
  availability : NONE
  usage/access : UNKNOWN / UNKNOWN
  pass/enc.key : no / no"""
    )

    # The repr may change in the future...
    assert str(deviceInfo_0) == repr(deviceInfo_0)

    deviceInfo_1 = kvrlib.structures.kvrDeviceInfo()
    deviceInfo_1.ean_hi = ct.c_uint32(1111)
    deviceInfo_1.ean_lo = ct.c_uint32(2222)
    deviceInfo_1.ser_no = ct.c_uint32(4444)

    # Checking __eq__ so we need != here
    assert deviceInfo_1 is not None  # noqa: E711

    assert deviceInfo_0 == deviceInfo_0
    assert not deviceInfo_0 == deviceInfo_1

    my_set = {deviceInfo_0}
    my_set.add(deviceInfo_1)
    my_set.add(deviceInfo_0)
    assert len(my_set) == 2

    # qqqmac Needs list for now...
    # my_info_list = kvrlib.structures.kvrDeviceInfoList(my_set)

    my_info_list = kvrlib.structures.kvrDeviceInfoList(
        [
            deviceInfo_0,
            deviceInfo_1,
        ]
    )
    assert (
        str(my_info_list)
        == """
name/hostname  : '' / ''
  ean/serial   : 457-8ae / 3333
  fw           : v0.0.000
  addr/cli/AP  : - (UNKNOWN) / - (UNKNOWN) / - (UNKNOWN)
  availability : NONE
  usage/access : UNKNOWN / UNKNOWN
  pass/enc.key : no / no

name/hostname  : '' / ''
  ean/serial   : 457-8ae / 4444
  fw           : v0.0.000
  addr/cli/AP  : - (UNKNOWN) / - (UNKNOWN) / - (UNKNOWN)
  availability : NONE
  usage/access : UNKNOWN / UNKNOWN
  pass/enc.key : no / no"""
    )


@pytest.mark.skip(reason="test needs device 00671-3, s/n 10545, on network")
@kvdeprecated
@winonly
def test_connect_disconnect_remote_device():
    """https://www.kvaser.com/developer-blog/using-python-connect-remote-device-2-3/"""

    from canlib import canlib, kvDevice

    rl = kvrlib.kvrlib()
    # qqqmac would be nice to use kvdevice here
    serialNo = 10545
    dev = kvDevice.kvDevice(ean='73-30130-00671-3', serial=serialNo)
    print(f"Connecting to device with serial number {serialNo}")
    addressList = kvrlib.kvrDiscovery.getDefaultAddresses(kvrlib.kvrAddressTypeFlag_BROADCAST)
    print(f"IP addresses to scan for devices on: {addressList}")

    discovery = rl.discoveryOpen()
    discovery.setAddresses(addressList)

    delay_ms = 100
    timeout_ms = 1000
    discovery.setScanTime(delay_ms, timeout_ms)

    print("Scanning devices...\n")
    deviceInfos = discovery.getResults()
    print(f"Scanning result:{deviceInfos}\n")
    for deviceInfo in deviceInfos:
        if deviceInfo.ser_no == serialNo:
            assert kvrlib.kvrlib().deviceGetServiceStatus(deviceInfo) == (12, 0)
            print(kvrlib.kvrlib().deviceGetServiceStatusText(deviceInfo))
            assert (
                kvrlib.kvrlib().deviceGetServiceStatusText(deviceInfo)
                == "Service: State=12 (STANDBY)"
            )
            deviceInfo.connect()
            print('Connecting to the following device:')
            print(deviceInfo)
            discovery.storeDevices(deviceInfos)
            break
    discovery.close()

    # Wait for our device to be able to connect in open()
    time.sleep(10)
    cl = canlib.canlib()
    cl.reinitializeLibrary()
    dev.open()
    dev.close()

    print("\nConnected devices:")
    device_found = False
    # for device in kvDevice.kvDevice.allDevices(reinitialize=False):
    for device in kvDevice.kvDevice.allDevices():
        print(device)
        if device._serial == serialNo:
            device_found = True
    assert device_found

    # testing some configuration on connected device
    cfg = kvrlib.kvrConfig(rl, channel=dev._channel)
    xml = cfg.getXml()
    print(xml)
    cfg.close()
    cfg.openEx(channel=dev._channel, mode=kvrlib.kvrConfig.MODE_RW)
    cfg.close()
    time.sleep(10)
    print("unloading...")
    rl.unload()
    cl = canlib.canlib()
    cl.unloadLibrary()
    time.sleep(10)
    cl.initializeLibrary()
    rl = kvrlib.kvrlib()

    # testing profile commands on connected device
    num_profiles = rl.configNoProfilesGet(channel=dev._channel)
    assert num_profiles == 4
    active_profile = rl.configActiveProfileGet(channel=dev._channel)
    assert active_profile == 0
    rl.configActiveProfileSet(channel=5, profile_number=active_profile)
    active_profile = rl.configActiveProfileGet(channel=dev._channel)
    assert active_profile == 0

    discovery = rl.discoveryOpen()
    discovery.setAddresses(addressList)

    print("Scanning devices...\n")
    deviceInfos = discovery.getResults()
    # print("Scanning result:%s\n" % deviceInfos)
    for deviceInfo in deviceInfos:
        if deviceInfo.ser_no == serialNo:
            deviceInfo.disconnect()
            print('Disconnecting to the following device:')
            print(deviceInfo)
            discovery.storeDevices(deviceInfos)
            break

    # Wait for our device to disappear
    time.sleep(10)
    device_found = True
    while device_found:
        device_found = False
        print("Sleeping Zzzz")
        time.sleep(5)
        for device in kvDevice.kvDevice.allDevices():
            print(device)
            if device._serial == serialNo:
                device_found = True
        assert device_found is False

    rl.unload()


@winonly
@pytest.mark.skip(reason='Device needed here...')
def test_dev_open_close():
    from canlib import kvDevice

    dev = kvDevice.kvDevice(ean='73-30130-00778-9', serial=1023)
    dev.open()
    for device in kvDevice.kvDevice.allDevices():
        print(device)
    # It was ok to close an invalid handle
    dev.close()


@winonly
@pytest.mark.skip(reason='Remote device needed on channel 0...')
def test_config_open():
    import canlib.kvrlib as kvrlib

    kl = kvrlib.kvrlib()
    kl.configOpen(channel=0)
    # Should test more here
