import io
import os
import os.path
import shutil
import sys
import time
from datetime import datetime

import pytest
from conftest import winonly,linuxonly
from kvprobe import features

from canlib import EAN, CanlibException, Device, Frame, VersionNumber, canlib


def test_version():
    v = canlib.dllversion()
    print(v)
    print(v.major, v.minor)


def test_list_devices():
    num_channels = canlib.getNumberOfChannels()
    print(f"Found {num_channels} channels")
    for ch in range(0, num_channels):
        chdata = canlib.ChannelData(ch)
        print(
            "%d. %s (%s / %s)"
            % (
                ch,
                chdata.channel_name,
                chdata.card_upc_no,
                chdata.card_serial_no,
            )
        )


def create_iocontrol_attribute_list():
    VALS = [
        ('timer_scale', (1500, 1000)),
        ('txack', (0, 1, 2)),
        ('rx_buffer_level', None),
        ('tx_buffer_level', None),
        ('clear_error_counters', None),
        ('txrq', (True, False)),
        ('eventhandle', None),
        ('driverhandle', None),
        ('report_access_errors', (True, False)),
        ('rx_queue_size', (100, 500, 1250)),
        ('buson_time_auto_reset', (False, True)),
        ('local_txecho', (True, False)),
        ('error_frames_reporting', (True, False)),
        ('channel_quality', None),
        ('roundtrip_time', None),
        ('bus_type', None),
        ('devname_ascii', None),
        ('time_since_last_seen', None),
        ('throttle_scaled', (0,)),  # Not supported by all devices (hence testing with 0 only)
        ('brlimit', (100, 1000, 0)),
        ('tx_interval', (0, 10, 234, 478, 829, 129)),
        ('prefer_ext', lambda: ()),
        ('prefer_std', lambda: ()),
        ('flush_rx_buffer', lambda: ()),
        ('flush_tx_buffer', lambda: ()),
        ('connect_to_virtual_bus', lambda: (1,)),  # test needs to find a virtual channel
        ('disconnect_from_virtual_bus', lambda: (1,)),
        ('reset_overrun_count', lambda: ()),
    ]
    # check that all attributes are represented in VALS
    val_keys = [x[0] for x in VALS]
    ioc_keys = list(canlib.iocontrol.ATTRIBUTES.keys())
    assert len(val_keys) == len(ioc_keys)
    for key in val_keys:
        assert key in ioc_keys
    return val_keys, VALS


def val_to_id(val):
    # Get first key, this is the same as 'list(val.keys())[0]'
    return next(iter(val))


@pytest.mark.parametrize(
    "iocontrol_attribute", create_iocontrol_attribute_list()[1], ids=val_to_id
)
def test_iocontrol(chA, iocontrol_attribute):
    name, value = iocontrol_attribute

    WINONLY = (
        'eventhandle',
        'driverhandle',
        'rx_queue_size',
        'error_frames_reporting',
        'channel_quality',
        'roundtrip_time',
        'bus_type',
        'devname_ascii',
        'time_since_last_seen',
        'throttle_scaled',
        'prefer_ext',
        'prefer_std',
        'connect_to_virtual_bus',
        'disconnect_from_virtual_bus',
    )
    if name in WINONLY and not sys.platform.startswith('win'):
        pytest.skip()

    VIRTUALONLY = ('connect_to_virtual_bus', 'disconnect_from_virtual_bus')
    if name in VIRTUALONLY and chA.channel_data.bus_type != canlib.BusTypeGroup.VIRTUAL:
        pytest.skip("Not connected to virtual channel.")

    print(f"{name}: {value}")

    ioc = chA.iocontrol
    if callable(value):
        # its a function
        args = value()
        print(f"{name}(*{args!r})")
        print("->", getattr(ioc, name)(*args))
    elif value is None:
        # value can't be set
        try:
            print(name, "->", getattr(ioc, name))
        # memorator (ean 00175-6)
        except canlib.exceptions.CanNotImplementedError:
            pass
        except canlib.exceptions.CanError as e:
            # memorator professional (ean 00351-4)
            if not (
                Device.find(channel_number=chA.index).ean == EAN("00351-4")
                and e.status == canlib.Error.HARDWARE
            ):
                raise
    else:
        for val in value:
            print(name, '<-', val)
            try:
                setattr(ioc, name, val)
            # memorator (ean 00175-6)
            except canlib.exceptions.CanNotImplementedError:
                pass
            try:
                _val = getattr(ioc, name)
            # memorator (ean 00175-6)
            except canlib.exceptions.CanNotImplementedError:
                pass
            except AttributeError:
                pass
            else:
                print('->', _val)
                assert _val == val
                if type(val) is bool:
                    assert type(_val) is bool


def create_channeldata_attribute_list():
    attribute_list = list(canlib.channeldata.ATTRIBUTES.keys())
    attribute_list += ['channel_name', 'custom_name']
    return attribute_list


@pytest.mark.parametrize("channeldata_attribute", create_channeldata_attribute_list())
def test_channeldata_attribute(channel_no, channeldata_attribute):
    WINONLY = (
        'bus_type',
        'channel_quality',
        'devdescr_unicode',
        'device_physical_position',
        'devname_ascii',
        'dll_file_version',
        'dll_filetype',
        'dll_product_version',
        'driver_file_version',
        'driver_product_version',
        'is_remote',
        'logger_type',
        'mfgname_unicode',
        'remote_host_name',
        'remote_mac',
        'remote_operational_mode',
        'remote_profile_name',
        'remote_type',
        'roundtrip_time',
        'time_since_last_seen',
        'timesync_enabled',
        'trans_cap',
        'trans_serial_no',
        'trans_upc_no',
        'ui_number',
    )
    if not sys.platform.startswith('win'):
        if channeldata_attribute in WINONLY:
            pytest.skip("Windows only test")
    REMOTE_ONLY = (
        'remote_host_name',
        'remote_operational_mode',
        'remote_mac',
        'remote_profile_name',
    )
    channeldata = canlib.ChannelData(channel_no)
    if channeldata_attribute in REMOTE_ONLY:
        # BLA-3264
        try:
            remote_type = channeldata.remote_type
        except canlib.exceptions.CanNotImplementedError:
            pytest.skip("canCHANNELDATA_REMOTE_TYPE is not implemented")
        if not remote_type:
            pytest.skip("Not a remote device")
    DEVICE_LIMITS = {'00241-8': ['hw_status', 'feature_ean']}
    product_ean = channeldata.card_upc_no.product()
    if product_ean in DEVICE_LIMITS.keys():
        if channeldata_attribute in DEVICE_LIMITS[product_ean]:
            pytest.skip(f"Device {product_ean} does not support {channeldata_attribute}")

    name = channeldata_attribute
    try:
        print(name, '->', repr(getattr(channeldata, name)))
    # memorator (ean 00175-6)
    except canlib.exceptions.CanNotImplementedError:
        pass
    except canlib.exceptions.CanError as e:
        # memorator professional (ean 00351-4)
        if not (Device.find(channel_number=channel_no).ean == EAN("00351-4") and e.status == -1):
            raise


def test_handle_data(chA):
    WINONLY = (
        'bus_type',
        'channel_quality',
        'devdescr_unicode',
        'device_physical_position',
        'devname_ascii',
        'dll_file_version',
        'dll_filetype',
        'dll_product_version',
        'driver_file_version',
        'driver_product_version',
        'is_remote',
        'logger_type',
        'mfgname_unicode',
        'remote_host_name',
        'remote_mac',
        'remote_operational_mode',
        'remote_profile_name',
        'remote_type',
        'roundtrip_time',
        'time_since_last_seen',
        'timesync_enabled',
        'trans_cap',
        'trans_serial_no',
        'trans_upc_no',
        'ui_number',
    )
    IGNORED = (
        'remote_type',  # Wrong in BBv2
        'remote_operational_mode',  # returns A hardware error was detected
        # (-15) (unless BBv2)
        'is_remote',  # Returns Not implemented
        'remote_profile_name',  # Returns -15
        'remote_host_name',  # Returns -15 (unless BBv2)
        'remote_mac',  # Returns -15 (unless BBv2)
        'logger_type',  # Wrong in BBv2
        'feature_ean',  # Wrong in BBv2
    )
    channeldata = canlib.HandleData(chA)

    for name in canlib.channeldata.ATTRIBUTES:
        if name in WINONLY and not sys.platform.startswith('win'):
            continue
        elif name in IGNORED:
            continue
        try:
            print(name, '->', repr(getattr(channeldata, name)))
        # memorator (ean 00175-6)
        except canlib.exceptions.CanNotImplementedError:
            pass
        except canlib.exceptions.CanError as e:
            # memorator professional (ean 00351-4)
            if e.status == -1 and not chA.channel_data.card_upc_no == EAN("00351-4"):
                raise

    print('custom_name', '->', repr(channeldata.custom_name))


def test_use_max_bitrate(channel_no):
    chdata = canlib.ChannelData(channel_no)
    default_brlimit = chdata.max_bitrate
    print("max bps:", default_brlimit)

    ch = canlib.openChannel(channel_no)

    if default_brlimit == 0:
        # devices not supporting max_bitrate returns 0......
        new_brlimit = default_brlimit + 100
    else:
        new_brlimit = default_brlimit - 100
    ch.iocontrol.brlimit = new_brlimit
    assert chdata.max_bitrate == new_brlimit

    new_brlimit = 0
    ch.iocontrol.brlimit = new_brlimit
    assert chdata.max_bitrate == default_brlimit
    ch.close()


def test_read_timeout(chA):
    chA.busOn()
    now = datetime.now()
    with pytest.raises(canlib.CanNoMsg):
        chA.read(timeout=200)
    time_passed = datetime.now() - now
    assert time_passed.microseconds > 190000  # tested in test/ktest/read_wait


def test_write_timeout(chA):
    chA.busOn()
    with pytest.raises(CanlibException) as e:
        chA.writeWait(Frame(id_=4, data=b''), timeout=0)
    assert e.value.status == canlib.Error.TIMEOUT


def test_txack_onoff(chA, chB):
    # This particular device defaults to silent mode currently (BLB-1582)
    if Device.find(channel_number=chA.index).ean == EAN("00351-4"):
        chA.setBusOutputControl(canlib.Driver.NORMAL)
    if Device.find(channel_number=chB.index).ean == EAN("00351-4"):
        chB.setBusOutputControl(canlib.Driver.NORMAL)
    chA.busOn()
    chB.busOn()

    ioc0 = chA.iocontrol
    ioc0.txack = True

    chA.writeWait(Frame(id_=4, data=b''), timeout=100)
    chA.read()

    ioc0.txack = False
    chA.writeWait(Frame(id_=5, data=b''), timeout=100)
    with pytest.raises(canlib.CanNoMsg):
        chA.read()

    ioc0.txack = True
    chA.writeWait(Frame(id_=4, data=b''), timeout=100)
    chA.read()

    chA.busOff()
    chB.busOff()


@pytest.mark.parametrize("auto_reset", [True, False])
def test_buson_time(chA, chB, auto_reset):
    print('auto_reset:', auto_reset)
    canlib.IOControl(chA).buson_time_auto_reset = auto_reset
    t_a = [chA.readTimer()]
    t_b = [chB.readTimer()]

    assert t_a == pytest.approx(t_b, abs=5)

    time.sleep(0.5)
    t_a.append(chA.readTimer())
    t_b.append(chB.readTimer())
    assert t_a[-1] == pytest.approx(t_a[-2] + 500, abs=150)
    assert t_b[-1] == pytest.approx(t_b[-2] + 500, abs=150)

    chA.busOn()
    t_a.append(chA.readTimer())
    t_b.append(chB.readTimer())
    if auto_reset:
        assert t_a[-1] == pytest.approx(11, abs=100)
    else:
        assert t_a[-1] == pytest.approx(t_a[-2] + 15, abs=100)
    assert t_b[-1] == pytest.approx(t_b[-2] + 15, abs=100)
    print('time ChA:', t_a)
    print('time ChB:', t_b)


def test_txecho_onoff(channel_no_pair):
    CHANNEL, CHANNEL_TWO = channel_no_pair
    ch0a = canlib.openChannel(CHANNEL)
    ch0b = canlib.openChannel(CHANNEL)
    chB = canlib.openChannel(CHANNEL_TWO)

    # For some models, the following lines are required
    ch0a.setBusOutputControl(canlib.Driver.NORMAL)
    ch0a.setBusParams(canlib.canBITRATE_1M)
    chB.setBusOutputControl(canlib.Driver.NORMAL)
    chB.setBusParams(canlib.canBITRATE_1M)

    ch0a.busOn()
    ch0b.busOn()
    chB.busOn()

    ioc = ch0b.iocontrol
    ioc.local_txecho = True

    ch0a.writeWait(Frame(id_=4, data=b''), timeout=1000)
    print("B", ch0b.read())

    ioc.local_txecho = False

    ch0a.writeWait(Frame(id_=5, data=b''), timeout=100)
    with pytest.raises(canlib.CanNoMsg):
        print("B", ch0b.read())

    ch0a.busOff()
    chB.busOff()
    ch0a.close()
    ch0b.close()
    chB.close()


def test_can_channel_flags(channel_no):
    channeldata = canlib.ChannelData(channel_no)
    print('card_upc_no', '->', repr(channeldata.card_upc_no))
    print('channel_flags', '->', repr(channeldata.channel_flags))
    # Flags are remembered, so we can't test this now...
    # assert channeldata.channel_flags == 0

    print(f'Opening channel {channel_no} as CAN')
    ch = canlib.openChannel(channel_no)
    assert channeldata.channel_flags == 0
    ch.busOn()
    assert channeldata.channel_flags == canlib.ChannelFlags.IS_OPEN
    ch.busOff()
    ch.close()


@pytest.mark.feature(features.canfd)
def test_canfd_channel_flags(channel_no):
    channeldata = canlib.ChannelData(channel_no)
    print('card_upc_no', '->', repr(channeldata.card_upc_no))
    print('channel_flags', '->', repr(channeldata.channel_flags))
    # Flags are remembered, so we can't test this now...
    # assert channeldata.channel_flags == 0

    print(f'Opening channel {channel_no} as CAN FD')
    ch = canlib.openChannel(channel_no, flags=canlib.Open.CAN_FD)
    assert channeldata.channel_flags == canlib.ChannelFlags.IS_CANFD
    ch.busOn()
    assert channeldata.channel_flags == (
        canlib.ChannelFlags.IS_CANFD | canlib.ChannelFlags.IS_OPEN
    )
    ch.busOff()
    ch.close()
    assert channeldata.channel_flags == canlib.ChannelFlags.IS_CANFD


def test_data_bitrate_no_canfd(channel_no):
    with pytest.raises(TypeError):
        _ = canlib.openChannel(channel_no, 0, None, canlib.canFD_BITRATE_1M_80P)


@pytest.mark.feature(features.canfd)
def test_canfd_no_data_bitrate(channel_no):
    with pytest.raises(ValueError):
        canlib.openChannel(channel_no, canlib.Open.CAN_FD, canlib.canFD_BITRATE_1M_80P, None)


def test_txe(datadir):
    example_txe_file = os.path.join(datadir, 'txe', 'example.txe')

    def _file_to_source(name):
        path = os.path.join(datadir, 'txe', name)
        with io.open(path, encoding='utf-8') as f:
            return f.read().splitlines()

    expected_sources = dict((name, _file_to_source(name)) for name in ['example.t', 'util.t'])

    txe = canlib.Txe(example_txe_file)
    assert txe.path == example_txe_file
    assert txe.file_version == VersionNumber(major=1, minor=0, build=0)
    assert txe.compiler_version == VersionNumber(major=3, minor=7, build=423)
    assert txe.date == datetime(2018, 3, 15, 9, 22, 36)
    assert txe.description == 'A hello world script!'
    assert txe.is_encrypted is False
    assert txe.size_of_code == 344

    actual_sources = dict((name, contents.splitlines()) for name, contents in txe.source)
    assert actual_sources == expected_sources


def test_txe_no_description_or_source(datadir):
    stripped_txe_file = os.path.join(datadir, 'txe', 'example_no_description_or_source.txe')
    txe = canlib.Txe(stripped_txe_file)
    assert txe.description == ''
    assert txe.is_encrypted is False
    assert list(txe.source) == []


def test_txe_encrypted(datadir):
    encrypted_txe_file = os.path.join(datadir, 'txe', 'example_encrypted.txe')
    txe = canlib.Txe(encrypted_txe_file)
    assert txe.path == encrypted_txe_file
    assert txe.description == 'A hello world script!'
    assert txe.is_encrypted
    assert txe.size_of_code == 344
    with pytest.raises(canlib.TxeFileIsEncrypted, match=r'encrypted'):
        list(txe.source)


def test_txe_not_supported_version(datadir):
    not_supported_version_txe_file = os.path.join(datadir, 'txe', 'not_supported_version.txe')
    txe = canlib.Txe(not_supported_version_txe_file)
    with pytest.raises(canlib.CanError) as excinfo:
        assert txe.file_version == VersionNumber(major=1, minor=1, build=0)
    assert excinfo.value.status == -41


def test_txe_wrong_magic(datadir):
    not_supported_version_txe_file = os.path.join(datadir, 'txe', 'wrong_magic.txe')
    txe = canlib.Txe(not_supported_version_txe_file)
    with pytest.raises(canlib.CanError) as excinfo:
        assert txe.file_version == VersionNumber(major=1, minor=1, build=0)
    assert excinfo.value.status == -42


def test_txe_simplified_chinese_path(datadir, tmpdir):
    example_txe_file = os.path.join(datadir, 'txe', 'example.txe')
    zh_cn_txe_file = tmpdir.join(u'\u5723\u8bde\u8001\u4eba.txe').strpath
    shutil.copy(example_txe_file, zh_cn_txe_file)
    txe = canlib.Txe(zh_cn_txe_file)
    assert txe.path == zh_cn_txe_file
    assert txe.file_version == VersionNumber(major=1, minor=0, build=0)


@winonly
def test_notify_callback_py27(channel_no):
    callback_has_been_called = {'y': False}

    def callback_func(hnd, context, event):
        event = canlib.Notify(event)
        print(f"Callback function called, context:{context}, event:{event!r}")
        callback_has_been_called['y'] = True

    callback = canlib.dll.KVCALLBACK_T(callback_func)

    with canlib.openChannel(channel_no) as ch:
        ch.set_callback(callback, context=121, event=canlib.Notify.BUSONOFF)
        ch.busOn()
        time.sleep(0.5)
    assert callback_has_been_called['y']


def test_report_access_errors(channel_no):
    with canlib.openChannel(0) as ch_with_access:
        canlib.IOControl(ch_with_access).report_access_errors = True
        ch_with_access.busOff()
        ch_with_access.setBusParams(canlib.canBITRATE_50K)
        ch_with_access.busOn()
        with canlib.openChannel(0) as ch_without_access:
            canlib.IOControl(ch_without_access).report_access_errors = True
            ch_without_access.busOn()
            with pytest.raises(canlib.CanError):
                ch_without_access.setBusParams(canlib.canBITRATE_500K)


def test_init_access(channel_no):
    with canlib.openChannel(0) as ch_with_access:
        canlib.IOControl(ch_with_access).report_access_errors = True
        ch_with_access.busOff()
        ch_with_access.setBusParams(canlib.canBITRATE_50K)
        ch_with_access.busOn()
        with pytest.raises(canlib.CanError):
            with canlib.openChannel(0, flags=canlib.Open.REQUIRE_INIT_ACCESS):
                pass


def test_no_init_access(channel_no):
    # Reset channel CAN mode, this is a workaround for bug BLA-3663?
    with canlib.openChannel(channel_no) as _:
        pass
    with canlib.openChannel(channel_no, flags=canlib.Open.NO_INIT_ACCESS) as ch_without_access:
        canlib.IOControl(ch_without_access).report_access_errors = True
        ch_without_access.busOff()
        with pytest.raises(canlib.CanError):
            ch_without_access.setBusParams(canlib.canBITRATE_50K)
            ch_without_access.busOn()
        with canlib.openChannel(channel_no) as ch_with_access:
            canlib.IOControl(ch_with_access).report_access_errors = True
            ch_with_access.setBusParams(canlib.canBITRATE_500K)
            ch_with_access.busOn()


@linuxonly
@pytest.mark.xfail
@pytest.mark.feature(features.canfd)
def test_no_init_access_bug_bla_3663(channel_no):
    # Open a channel in FD mode
    with canlib.openChannel(channel_no, flags=canlib.Open.CAN_FD) as ch_with_access:
        with canlib.openChannel(channel_no, flags=canlib.Open.NO_INIT_ACCESS) as ch_without_access:
            # Due to linux implementation the NO_INIT_ACCESS handle has now
            # "locked" the channel in CAN_FD mode.
            ch_with_access.close()
            with canlib.openChannel(channel_no) as _:
                pass

# There's currently no way to parametrize with fixtures, so we do
# a workaround by manually instantiating two tests.
# https://github.com/pytest-dev/pytest/issues/349


@pytest.mark.parametrize("min_num_msg", [1, 10, 100])
def test_bus_statistics_CAN(chA, chB, min_num_msg):
    bus_statistics(chA, chB, min_num_msg)


def test_read_error_counters(chA):
    error_counters = chA.read_error_counters()
    assert error_counters.rx == 0
    assert error_counters.tx == 0
    assert error_counters.overrun == 0


def bus_statistics(ch0, ch1, min_num_msg):
    NUM_OF_STD = min_num_msg
    NUM_OF_EXT = min_num_msg + 10
    NUM_OF_STDRTR = min_num_msg + 20
    NUM_OF_EXTRTR = min_num_msg + 30

    chA, chB = ch0, ch1

    chA.busOn()
    chB.busOn()

    frames = [
        (NUM_OF_STD, Frame(id_=4, data=b'4', flags=canlib.MessageFlag.STD)),
        (NUM_OF_EXT, Frame(id_=40, data=b'40', flags=canlib.MessageFlag.EXT)),
        (
            NUM_OF_STDRTR,
            Frame(id_=5, data=b'\x00', flags=canlib.MessageFlag.STD | canlib.MessageFlag.RTR),
        ),
        (
            NUM_OF_EXTRTR,
            Frame(id_=5, data=b'\x00', flags=canlib.MessageFlag.EXT | canlib.MessageFlag.RTR),
        ),
    ]
    for num_of_msg, frame in frames:
        for _ in range(num_of_msg):
            chA.write(frame)

        for _ in range(num_of_msg):
            assert frame == chB.read(timeout=200)
    statistics = chA.get_bus_statistics()
    print("A channel")
    print(
        "stdData:",
        statistics.stdData,
        "stdRemote:",
        statistics.stdRemote,
        "extData:",
        statistics.extData,
        "extRemote:",
        statistics.extRemote,
        "errFrame:",
        statistics.errFrame,
        "busLoad:",
        statistics.busLoad,
        "overruns:",
        statistics.overruns,
    )
    print("B channel:")
    statisticsB = chB.get_bus_statistics()
    print(
        "stdData:",
        statisticsB.stdData,
        "stdRemote:",
        statisticsB.stdRemote,
        "extData:",
        statisticsB.extData,
        "extRemote:",
        statisticsB.extRemote,
        "errFrame:",
        statisticsB.errFrame,
        "busLoad:",
        statisticsB.busLoad,
        "overruns:",
        statisticsB.overruns,
    )

    assert statistics.stdData == NUM_OF_STD
    assert statistics.extData == NUM_OF_EXT
    assert statistics.stdRemote == NUM_OF_STDRTR
    assert statistics.extRemote == NUM_OF_EXTRTR

    assert statisticsB.stdData == NUM_OF_STD
    assert statisticsB.extData == NUM_OF_EXT
    assert statisticsB.stdRemote == NUM_OF_STDRTR
    assert statisticsB.extRemote == NUM_OF_EXTRTR

    chA.busOff()
    chB.busOff()

    statistics = chA.get_bus_statistics()
    statisticsB = chB.get_bus_statistics()

    assert statistics.stdData == 0
    assert statistics.extData == 0
    assert statistics.stdRemote == 0
    assert statistics.extRemote == 0

    assert statisticsB.stdData == 0
    assert statisticsB.extData == 0
    assert statisticsB.stdRemote == 0
    assert statisticsB.extRemote == 0

    chA.busOn()
    chB.busOn()


@pytest.mark.feature(features.virtual)
@pytest.mark.parametrize("min_num_msg", [10, 100])
def test_bus_statistics_virtual_CAN(chA, chB, min_num_msg):
    bus_statistics(chA, chB, min_num_msg)


@pytest.mark.skip("Test only works with dinrail that has storage")
def test_file_disk_format(datadir, channel_no):
    file_name = 'example.txe'
    dummy_file = os.path.join(datadir, 'txe', file_name)
    with canlib.openChannel(channel=channel_no) as ch:
        ch.fileCopyToDevice(hostFileName=dummy_file, deviceFileName=file_name)
        file_count = ch.fileGetCount()
        assert file_count == 1
        _ = ch.fileDiskFormat()
        file_count = ch.fileGetCount()
        assert file_count == 0
