import datetime
import filecmp
import os.path
from pathlib import Path

import pytest
from conftest import kvdeprecated
from kvprobe import features

import canlib.kvmlib as kvmlib
from canlib.frame import dlc_to_bytes

# untested functions:
# UnmountedLog.format_disk()
# Memorator.flash_leds()
# Memorator.rtc.setter

KMF_FILE_MHYDRA = os.path.join("kmf2", "LOG00000.KMF")


def print_events(log_file, num=5):
    num_seen = 0
    for event in log_file:
        print(event)
        num_seen += 1
        if num_seen >= num:
            break


@pytest.mark.feature(features.logger_v2)
def test_openDevice(channel_no):
    with kvmlib.openDevice(channel_no) as memo:
        print(memo.disk_size)
        print(memo.disk_usage)
        print(memo.serial_number)
        print(memo.rtc)

        memo.mount()
        assert memo.mounted
        assert isinstance(memo.log, kvmlib.MountedLog)
        memo.reopen()
        assert not memo.mounted
        assert isinstance(memo.log, kvmlib.UnmountedLog)


def test_openKmf(datadir):
    kmf_file = os.path.join(datadir, KMF_FILE_MHYDRA)
    with kvmlib.openKmf(kmf_file) as memo:
        print(memo.disk_usage)
        print(len(memo.log))
        assert len(memo.log) == 5
        for logfile in memo.log:
            print(logfile)
            print_events(logfile)


@pytest.mark.feature(features.logger_v2)
def test_swinfo(channel_no):
    with kvmlib.openDevice(channel_no) as memo:
        print(memo.config_version_needed)
        print(memo.driver_version)
        print(memo.firmware_version)
        print(memo.kvmlib_version)


@pytest.mark.feature(features.logger_v2)
def test_mount(channel_no):
    with kvmlib.openDevice(channel_no) as memo:
        print(memo.log)
        pre_mount_len = len(memo.log)
        print(pre_mount_len)
        assert memo.mounted is False

        memo.mount()

        print(memo.log)
        post_mount_len = len(memo.log)
        print(post_mount_len)
        assert memo.mounted is True

        assert pre_mount_len == post_mount_len


@pytest.mark.feature(features.logger_v2)
def test_dev_log_file_events(channel_no):
    with kvmlib.openDevice(channel_no, mount=True) as memo:
        print(len(memo.log))
        num = 0
        for log_file in memo.log:
            num += 1
            print(log_file)
            print(log_file.creator_serial)
            print(log_file.end_time)
            print(log_file.start_time)

            print_events(log_file)

        assert len(memo.log) == num


@pytest.mark.feature(features.logger_v2)
def test_dev_read_config(channel_no):
    with kvmlib.openDevice(channel_no) as memo:
        MemoClass = kvmlib.Memorator
        orig_assumed_size = MemoClass._ASSUMED_CONFIG_SIZE

        try:
            MemoClass._ASSUMED_CONFIG_SIZE = 1
            conf = memo.read_config()

            MemoClass._ASSUMED_CONFIG_SIZE = len(conf)
            assert memo.read_config() == conf

            MemoClass._ASSUMED_CONFIG_SIZE = len(conf) + 100
            assert memo.read_config() == conf
        finally:
            MemoClass._ASSUMED_CONFIG_SIZE = orig_assumed_size


@pytest.mark.feature(features.logger_v2)
def test_dev_read_write_config(channel_no):
    with kvmlib.openDevice(channel_no) as memo:
        conf = memo.read_config()
        memo.write_config(conf)


def test_logevent(datadir):
    kmf_file = os.path.join(datadir, KMF_FILE_MHYDRA)
    with kvmlib.openKmf(kmf_file) as memo:
        file0 = memo.log[0]

        it = iter(file0)
        ver_event = next(it)  # First event contain version information
        ver_mrte = ver_event._asMrtEvent()
        assert ver_event.serialNumber == ver_mrte.ver.serialNumber
        assert ver_event.lioMajor == ver_mrte.ver.lioMajor
        assert ver_event.lioMinor == ver_mrte.ver.lioMinor
        assert ver_event.fwMajor == ver_mrte.ver.fwMajor
        assert ver_event.fwMinor == ver_mrte.ver.fwMinor
        assert ver_event.fwBuild == ver_mrte.ver.fwBuild
        assert ver_event.eanHi == ver_mrte.ver.eanHi
        assert ver_event.eanLo == ver_mrte.ver.eanLo
        mlee = kvmlib.memoLogEventEx(ver_mrte)
        print("memoLogEventEx:", mlee)

        rtc_event = next(it)  # Second event contain RTC information
        rtc_mrte = rtc_event._asMrtEvent()
        assert rtc_event.calendartime == datetime.datetime.fromtimestamp(rtc_mrte.rtc.calendarTime)
        assert rtc_event.timeStamp == rtc_mrte.rtc.timeStamp
        mlee = kvmlib.memoLogEventEx(rtc_mrte)
        print("memoLogEventEx:", mlee)

        trig_event = next(it)  # Third event contain a trigger
        trig_mrte = trig_event._asMrtEvent()
        assert trig_event.timeStamp == trig_mrte.trig.timeStampLo + (
            trig_mrte.trig.timeStampHi << 16
        )
        assert trig_event.type == trig_mrte.trig.type
        assert trig_event.posttrigger == trig_mrte.trig.postTrigger
        assert trig_event.pretrigger == trig_mrte.trig.preTrigger
        assert trig_event.trigno == trig_mrte.trig.trigNo
        mlee = kvmlib.memoLogEventEx(trig_mrte)
        print("memoLogEventEx:", mlee)

        msg_event = next(it)  # Next event contain a message
        msg_mrte = msg_event._asMrtEvent()
        assert msg_event.id == msg_mrte.msg.id
        assert msg_event.timeStamp == msg_mrte.msg.timeStamp
        assert msg_event.channel == msg_mrte.msg.channel
        assert msg_event.dlc == msg_mrte.msg.dlc
        assert msg_event.flags == msg_mrte.msg.flags
        num_bytes = dlc_to_bytes(msg_mrte.msg.dlc, canFd=True)
        assert msg_event.data == bytearray(msg_mrte.msg.data[:num_bytes])

        frame = msg_event.asframe()
        assert frame.id == msg_event.id
        assert frame.timestamp == msg_event.timeStamp
        assert frame.dlc == msg_event.dlc
        assert frame.flags == msg_event.flags
        assert frame.data == msg_event.data

        mlee = kvmlib.memoLogEventEx(msg_mrte)
        print("memoLogEventEx:", mlee)


def test_logfile_iteration_protection(datadir):
    kmf_file = os.path.join(datadir, KMF_FILE_MHYDRA)
    with kvmlib.openKmf(kmf_file) as memo:
        assert len(memo.log) >= 2, "test requires at least two log files"

        # grab the two log files we're going to use
        file0 = memo.log[0]
        file1 = memo.log[1]

        it = iter(file0)
        # the log file is neither mounted nor is the container "locked" before one
        # value has been retrieved -- which is actually a nice feature
        next(it)
        assert memo.log._mounted_index == file0.index

        with pytest.raises(kvmlib.LockedLogError):
            file1._remount()

        it.close()
        file1._remount()


@kvdeprecated
def test_getVersion():
    ml = kvmlib.kvmlib()
    v = ml.getVersion()
    print(v)
    print(v.major, v.minor, v.build)


def test_version():
    v = kvmlib.dllversion()
    print(v)
    print(v.major, v.minor)


data_set = {
    'KME24': {
        'filename': Path("short-burst") / "logfile003.kme",
        'file_type': kvmlib.FileType.KME24,
    },
    'KME25': {
        'filename': Path("short-burst") / "logfile003.kme25",
        'file_type': kvmlib.FileType.KME25,
    },
    'KME40': {
        'filename': Path("short-burst") / "logfile003.kme40",
        'file_type': kvmlib.FileType.KME40,
    },
    'KME50': {
        'filename': Path("short-burst") / "logfile003.kme50",
        'file_type': kvmlib.FileType.KME50,
    },
    'KME60': {
        'filename': Path("short-burst") / "logfile003.kme60",
        'file_type': kvmlib.FileType.KME60,
    }
}


@pytest.mark.parametrize('stimuli', data_set.values(), ids=data_set.keys())
def test_kme_file_type(datadir, stimuli):
    filename = Path(datadir) / stimuli['filename']
    type = kvmlib.kme_file_type(filename)
    assert type == stimuli['file_type']


def test_kme_file_type_empty_file(datadir):
    filename = Path(datadir) / "empty.txt"
    with pytest.raises(kvmlib.kvmError):
        _ = kvmlib.kme_file_type(filename)


def test_kme_file_type_filename_as_str(datadir):
    # It should be possible to use strings as input as well
    # We are also using the obsolete constant here...
    filename = os.path.join(datadir, "short-burst", "logfile003.kme50")
    type = kvmlib.kme_file_type(filename)
    assert type == kvmlib.FileType.KME50


# Writing not supported for kme40, kme25, or kme
data_set = {
    'KME50': {
        'filename': Path("short-burst") / "logfile003.kme50",
        'kme_type': kvmlib.FileType.KME50,
    },
    'KME60': {
        'filename': Path("short-burst") / "logfile003.kme60",
        'kme_type': kvmlib.FileType.KME60,
    },
}


@pytest.mark.parametrize('stimuli', data_set.values(), ids=data_set.keys())
def test_kme_rw(datadir, tmpdir, stimuli):
    src_name = Path(datadir) / stimuli['filename']
    kme_type = stimuli['kme_type']
    dest_name = str(tmpdir.join(f"test_kme_creation.{stimuli['kme_type'].name.lower()}"))

    with kvmlib.openKme(str(src_name), filetype=kme_type) as src:
        with kvmlib.createKme(dest_name, filetype=kme_type) as dest:
            num_events = src.event_count_estimation()
            print(f'{src_name} contains about {num_events} events.')
            for event in src:
                print(event)
                dest.write_event(event)

    assert filecmp.cmp(src_name, src_name, shallow=False)
    assert filecmp.cmp(src_name, dest_name, shallow=False)


@kvdeprecated
def test_event_equility():
    x = kvmlib.logMsg(id=5, channel=1, dlc=9)
    y = kvmlib.logMsg(id=None, channel=None, dlc=None)
    assert x == y

    x = kvmlib.rtcMsg()
    y = kvmlib.trigMsg(type=2, trigno=1)
    assert x != y

    a = kvmlib.logMsg(id=5, channel=1, dlc=9)
    b = kvmlib.logMsg(id=5, channel=1, dlc=9)
    assert a == b

    c = kvmlib.MessageEvent(id=5, channel=1, dlc=9)
    assert a == c
