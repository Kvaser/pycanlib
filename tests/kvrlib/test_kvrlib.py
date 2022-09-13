import ctypes as ct
import os
import sys
import time

import pytest
from conftest import winonly

from canlib import EAN, canlib, kvDevice

"""Run using pytest, e.g. pytest --cov --cov-report html"""

if sys.platform.startswith('win'):
    from canlib import kvrlib
else:
    kvrlib = NotImplemented


@winonly
def test_import_kvrlib():
    version = kvrlib.dllversion()
    print(version)
    print(version.major)
    print(version.minor)


@winonly
def test_ean2ean_hi():
    ean_hi = kvrlib.ean2ean_hi("73-30130-00671-3")
    assert ean_hi == 0x73301


@winonly
def test_ean2ean_lo():
    ean_lo = kvrlib.ean2ean_lo("73-30130-00671-3")
    assert ean_lo == 0x30006713


@winonly
def test_ean_hi_lo2ean():
    ean = kvrlib.ean_hi_lo2ean(0x73301, 0x30006713)
    assert ean == "73-30130-00671-3"


@winonly
def test_address_string():
    addr = kvrlib.addressFromString(kvrlib.kvrAddress.Type_IPV4_PORT, "192.168.1.1:8080")
    # qqqmac fails...
    # assert str(addr) == "192.168.1.1:8080 (IPV4_PORT)"
    assert kvrlib.stringFromAddress(addr) == "192.168.1.1:8080"
    addr = kvrlib.addressFromString(kvrlib.kvrAddress.Type_IPV4, "192.168.10.1")
    print(addr)
    assert str(addr) == "192.168.10.1 (IPV4)"
    assert kvrlib.stringFromAddress(addr) == "192.168.10.1"


@winonly
def test_kvrConfig():
    with pytest.raises(kvrlib.KvrError):
        kvrlib.kvrConfig(password="Bulle")


@pytest.mark.skip(reason="test needs a device on network")
@winonly
def test_discovery_scan():
    print("Scanning for devices")
    addressList = kvrlib.kvrDiscovery.getDefaultAddresses(kvrlib.kvrAddressTypeFlag_BROADCAST)
    print(f"IP addresses to scan for devices on: {addressList}")

    discovery = kvrlib.kvrDiscovery()
    discovery.setAddresses(addressList)

    print("Scanning devices...\n")
    # qqqmac Can we convert discovery.getResults() into an iterator?
    # qqqmac ...not backwards compatible...
    deviceInfos = discovery.getResults()
    # We should get at least one hit
    assert len(deviceInfos) > 0
    print(f"Scanning result:{deviceInfos}\n")

    # qqqmac should we be able to use the with statement for discovery?
    discovery.close()


@winonly
def test_unknown_error():
    with pytest.raises(kvrlib.KvrError) as excinfo:
        raise kvrlib.exceptions.KvrGeneralError(111)
    assert "Unknown error text (111)" in str(excinfo.value)


@winonly
def test_kvrdeviceinfo():

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
    assert deviceInfo_1 is not None

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


@winonly
def test_profile_list(ldev):
    print("Device:", ldev)
    print("Num profiles:", len(ldev.profiles))
    assert len(ldev.profiles) > 0

    orig_active = ldev.active_profile
    print("Active profile:", ldev.active_profile)
    assert ldev.active_profile.profile_number < len(ldev.profiles)
    assert ldev.active_profile in ldev.profiles
    ldev.active_profile = ldev.profiles[-1]
    print("other profile set")
    time.sleep(2)
    assert ldev.active_profile.profile_number < len(ldev.profiles)
    assert ldev.active_profile in ldev.profiles
    ldev.active_profile = orig_active
    print("profile reset")
    time.sleep(2)


@winonly
def test_profile_read_write(ldev):
    conf = ldev.active_profile
    orig = conf.read()
    print(orig)

    conf.clear()
    time.sleep(2)
    assert conf.read() is None
    assert conf.info is None

    with open("tests/data/remote_conf.xml") as f:
        example = f.read()
    conf.write(example)
    time.sleep(2)
    assert repr(conf.read()) == repr(example)
    assert conf.info is not None

    conf.write(orig)
    time.sleep(2)


@winonly
@pytest.mark.skip(reason="qqqmac Not sure if we need an empty registry for this test")
def test_discovery():
    kvrlib.set_clear_stored_devices_on_exit(True)

    result = None
    with kvrlib.start_discovery(100, 1000) as disc:
        print("Discovery 1")
        for result in disc.results():
            print(result)
            print(result.info())

    if result:
        time.sleep(5)
        print(result.service_status)
        result.password = "hej"
        result.encryption_key = "kvaser11"

    with kvrlib.start_discovery(100, 1000) as disc:
        print("Discovery 2")
        for result in disc.results():
            print(result)
            # qqqmac This fails with:
            # assert <Availability.NONE: 0>
            #   +  where <Availability.NONE: 0> = <canlib.kvrlib.discovery.FoundDevice object at 0x000001DE20178C50>.stored
            assert result.stored


@winonly
def test_info_set():
    orig = kvrlib.stored_info_set()

    try:
        empty = kvrlib.empty_info_set()
        assert len(empty) == 0
        empty.store()
        assert empty == kvrlib.stored_info_set()

        empty.new_info(ean='01234-5', serial=42)
        assert len(empty) == 1
        empty.store()
        assert empty == kvrlib.stored_info_set()
        assert empty.find(ean='01234-5', serial=42)
        assert empty.find(ean=EAN('01234-5'), serial=42)

        empty.find_remove(ean=EAN('01234-5'), serial=42)
        assert len(empty) == 0
        empty.store()
        assert empty == kvrlib.stored_info_set()

        empty.new_info(ean='01234-5', serial=42)
        empty.new_info(ean='01234-5', serial=66)
        assert len(empty) == 2

        empty.clear()
        assert len(empty) == 0

    finally:
        orig.store()


@winonly
def test_discover_info_set():
    orig = kvrlib.stored_info_set()

    try:
        empty = kvrlib.empty_info_set()
        discovered = kvrlib.discover_info_set(10, 100, report_stored=False)
        if len(discovered) == 0:
            pytest.skip("No devices discovered.")

        random = discovered.pop()
        assert random not in discovered

        empty.add(random)
        assert random in empty

    finally:
        orig.store()


@winonly
def test_info_set_context():
    with kvrlib.stored_info_set():
        with kvrlib.empty_info_set() as empty:
            info = empty.new_info(ean='01234-5', serial=42, connect=True)
            assert info.connect is True
            info.connect = 3
            assert info.connect == 3
        assert kvrlib.stored_info_set() == empty


@winonly
def test_modify_DeviceInfo():
    vals = {
        'accessibility': kvrlib.Accessibility.PUBLIC,
        'client_address': kvrlib.Address(kvrlib.AddressType.IPV4, [192, 168, 1, 42]),
        'device_address': kvrlib.Address(kvrlib.AddressType.IPV4, [1, 2, 3, 4]),
        'ean': EAN('01234-5'),
        'serial': 42,
        'hostname': 'Dummy info',
        'name': 'Dummy',
    }
    info = kvrlib.DeviceInfo()
    info.update(vals)

    with pytest.raises(TypeError):
        info.ean = None
    with pytest.raises(TypeError):
        info.serial = None
    with pytest.raises(TypeError):
        info.accessibility = kvrlib.Error.CHECKSUM
    with pytest.raises(AttributeError):
        info.base_station_id = None
    with pytest.raises(TypeError):
        info.client_address = None
    with pytest.raises(TypeError):
        info.device_address = None


@winonly
def test_connection_test(ldev):
    test = ldev.connection_test()
    print(test.run(1))


@winonly
def test_config_info(ldev):
    info = ldev.active_profile.info
    print(info)


@winonly
def test_address_info(ldev):
    print(ldev.address_info)


@winonly
def test_connection_status(ldev):
    print(ldev.connection_status)


@winonly
def test_ldev_hostname(ldev):
    print(ldev.hostname)


@winonly
def test_wlan_scan(ldev):
    scan = ldev.wlan_scan()
    for r in scan:
        print(r)


@winonly
def test_generate_wep_keys():
    phrase = "test_generate_wep_keys"
    key64, key128 = kvrlib.generate_wep_keys(phrase)
    assert key64 == (b'20A8C639A6', b'7D4ECEA879', b'977D383562', b'592EF57854')
    assert key128 == b'517CA04C66AC584B7FBADE178B'


@winonly
def test_generate_wpa_keys():
    phrase = "test_generate_wpa_keys"
    ssid = "SSID"
    key = kvrlib.generate_wpa_keys(phrase, ssid)
    assert key == b'ED1E137783A0658A00EEC30CFD9BD8596CA2E1A367C8D2E4CEBE672CD848049C'


@winonly
def test_hostname():
    ean = EAN('00671-3')
    serial = 10545
    hostname = kvrlib.hostname(ean, serial)
    assert hostname == 'kv-06713-010545'


@winonly
def test_verify_xml(datadir):
    xml = "hej"
    # if the following two lines are removed, kvamemolibxml fails in
    # test_xmlGetValidationError (kvaXmlValidate())
    with open(os.path.join(datadir, "test01.xml")) as f:
        xml = f.read()

    err = kvrlib.verify_xml(xml)

    print(err)
    assert err == "Error in element 'VERSION' or 'PRODUCTFAMILY'."


@pytest.mark.skip(reason="test needs device 00671-3, s/n 10545, on network")
@winonly
def test_connect_disconnect_remote_device():
    """https://www.kvaser.com/developer-blog/using-python-connect-remote-device-2-3/"""

    # qqqmac would be nice to use official canlib.Device here
    serialNo = 10545
    dev = kvDevice.kvDevice(ean='73-30130-00671-3', serial=serialNo)
    print(f"Connecting to device with serial number {serialNo}")
    addressList = kvrlib.kvrDiscovery.getDefaultAddresses(kvrlib.kvrAddressTypeFlag_BROADCAST)
    print(f"IP addresses to scan for devices on: {addressList}")

    discovery = kvrlib.kvrDiscovery()
    # discovery.clearDevicesAtExit(True)
    discovery.setAddresses(addressList)

    delay_ms = 100
    timeout_ms = 10000
    discovery.setScanTime(delay_ms, timeout_ms)

    print("Scanning devices...\n")
    deviceInfos = discovery.getResults()
    print(f"Scanning result:{deviceInfos}\n")
    for deviceInfo in deviceInfos:
        if deviceInfo.ser_no == serialNo:
            deviceInfo.connect()
            print('Connecting to the following device:')
            print(deviceInfo)
            discovery.storeDevices(deviceInfos)
            break

    discovery.close()
    # Wait for our device to connect in open()
    time.sleep(10)
    canlib.reinitializeLibrary()
    dev.open()
    dev.close()

    print("\nConnected devices:")
    device_found = False
    for device in kvDevice.kvDevice.allDevices():
        print(device)
        if device._serial == serialNo:
            device_found = True
    assert device_found

    # testing some configuration on connected device
    cfg = kvrlib.kvrConfig(channel=dev._channel)
    # qqqmac kvrlib has a lot of auto open, and no auto close...
    xml = cfg.getXml()
    print(xml)
    cfg.close()
    cfg.openEx(channel=dev._channel, mode=kvrlib.kvrConfig.MODE_RW)
    cfg.close()
    time.sleep(10)
    print("unloading...")
    kvrlib.unload()
    canlib.unloadLibrary()
    time.sleep(10)
    canlib.initializeLibrary()

    # testing profile commands on connected device
    kvrlib.initializeLibrary()
    num_profiles = kvrlib.configNoProfilesGet(channel=dev._channel)
    assert num_profiles == 4
    active_profile = kvrlib.configActiveProfileGet(channel=dev._channel)
    assert active_profile == 0
    kvrlib.configActiveProfileSet(channel=5, profile_number=active_profile)
    active_profile = kvrlib.configActiveProfileGet(channel=dev._channel)
    assert active_profile == 0

    service_status = kvrlib.deviceGetServiceStatus(deviceInfo)
    print(f"service status:{service_status}")
    assert service_status == (6, 0)
    service_status_text = kvrlib.deviceGetServiceStatusText(deviceInfo)
    print(service_status_text)
    assert service_status_text == "Service: State=6 (CONNECTION UP)"

    discovery = kvrlib.kvrDiscovery()
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

    kvrlib.unload()


# qqqmac move to test_kvdevice.py
@winonly
@pytest.mark.skip(reason='Device needed here...')
def test_dev_open_close():
    dev = kvDevice.kvDevice(ean='73-30130-00778-9', serial=1023)
    dev.open()
    for device in kvDevice.kvDevice.allDevices():
        print(device)
    # qqqmac Why is handle invalid here?
    dev.close()
