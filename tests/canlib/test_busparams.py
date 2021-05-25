import collections

import pytest
from kvprobe import features

from canlib import canlib


# We need a device with new busparams API (BLB-2013), let's use canfd feature for now...
@pytest.mark.feature(features.canfd)
def test_set_busparams_tq(chA):
    expected_params = canlib.busparams.BusParamsTq(
        tq=80,
        phase1=8,
        phase2=8,
        sjw=2,
        prescaler=2,
        prop=63,
    )
    chA.set_bus_params_tq(expected_params)
    actual_params, _ = chA.get_bus_params_tq()
    assert actual_params == expected_params


@pytest.mark.feature(features.canfd)
def test_set_busparams_tq_fd(channel_no):
    with canlib.openChannel(channel_no, flags=canlib.Open.CAN_FD) as chA:
        expected_nominal = canlib.busparams.BusParamsTq(
            tq=80,
            phase1=8,
            phase2=8,
            sjw=2,
            prescaler=2,
            prop=63,
        )
        expected_data = canlib.busparams.BusParamsTq(
            tq=40,
            phase1=31,
            phase2=8,
            sjw=2,
            prescaler=2,
        )
        chA.set_bus_params_tq(nominal=expected_nominal, data=expected_data)
        actual_nominal, actual_data = chA.get_bus_params_tq()
        assert actual_nominal == expected_nominal
        assert actual_data == expected_data


@pytest.mark.feature(features.canfd)
def test_set_bus_params_tq_in_openchannel(channel_no):
    expected_nominal = canlib.busparams.BusParamsTq(
        tq=80,
        phase1=8,
        phase2=8,
        sjw=2,
        prescaler=2,
        prop=63,
    )
    expected_data = canlib.busparams.BusParamsTq(
        tq=40,
        phase1=31,
        phase2=8,
        sjw=2,
        prescaler=2,
    )
    with canlib.openChannel(
        channel_no,
        flags=canlib.Open.CAN_FD,
        bitrate=expected_nominal,
        data_bitrate=expected_data,
    ) as chA:
        actual_nominal, actual_data = chA.get_bus_params_tq()
        assert actual_nominal == expected_nominal
        assert actual_data == expected_data


def test_clock_info_invalid_version():
    """Test that given an unknown version number as input, an exception is raised."""
    clock_values_invalid_version = [12, 80, 1, 6, 100]
    with pytest.raises(ValueError):
        canlib.busparams.ClockInfo.from_list(clock_values_invalid_version)


def test_clock_info_contents():
    """Test that creating a ClockInfo gives correct values."""
    clock_values = [1, 80, 1, 6, 100]
    clock_info = canlib.busparams.ClockInfo.from_list(clock_values)
    assert str(clock_info) == (
        "ClockInfo(numerator=80, denominator=1, power_of_ten=6,"
        " accuracy=100), (frequency: 80.0 MHz)"
    )


@pytest.mark.parametrize(
    "clock_1, clock_2",
    [
        ([1, 80, 1, 6, 101], [1, 80, 1, 6, 100]),
        ([1, 80, 1, 7, 100], [1, 80, 1, 6, 100]),
        ([1, 80, 2, 6, 100], [1, 80, 1, 6, 100]),
        ([1, 81, 1, 6, 100], [1, 80, 1, 6, 100]),
    ],
)
def test_clock_info_differs(clock_1, clock_2):
    """Test that different values in ClockInfo makes them unequal."""
    clock_info_1 = canlib.busparams.ClockInfo.from_list(clock_1)
    clock_info_2 = canlib.busparams.ClockInfo.from_list(clock_2)
    assert clock_info_1 != clock_info_2


def test_clock_info_equal():
    """Test that different values in ClockInfo makes them unequal."""
    clock_info_1 = canlib.busparams.ClockInfo.from_list([1, 83, 1, 6, 101])
    clock_info_2 = canlib.busparams.ClockInfo.from_list([1, 83, 1, 6, 101])
    assert clock_info_1 == clock_info_2


def test_clock_info_eq_fail():
    """Test that different values in ClockInfo makes them unequal."""
    clock_info_1 = canlib.busparams.ClockInfo.from_list([1, 83, 1, 6, 101])
    clock_info_2 = canlib.busparams.ClockInfo
    assert clock_info_1 != clock_info_2


# We need a device with new busparams API (BLB-2013), let's use canfd feature for now...
@pytest.mark.feature(features.canfd)
def test_clock_info_correct(channel_no):
    """Test that reading ClockInfo from a device gives correct values."""
    chd = canlib.ChannelData(channel_no)
    expected_clock_info = canlib.busparams.ClockInfo(
        numerator=80, denominator=1, power_of_ten=6, accuracy=100
    )
    clock_info = chd.clock_info
    assert clock_info.frequency() == expected_clock_info.frequency()
    assert clock_info == expected_clock_info


TargetValues = collections.namedtuple(
    'TargetValues', 'bitrate sync_jump_width sample_point prop prescaler'
)
ExpectedValues = collections.namedtuple(
    'ExpectedValues', 'bitrate sync_jump_width sample_point' ' tq prop phase1 phase2 sjw prescaler'
)


def test_calc_bitrate():
    bitrate, tq = canlib.busparams.calc_bitrate(100, 100)
    assert bitrate == 33.333333333333336
    assert tq == 3


@pytest.mark.parametrize(
    "target, expected",
    [
        (
            TargetValues(
                bitrate=470_000,
                sync_jump_width=33.5,
                sample_point=82,
                prop=None,
                prescaler=1,
            ),
            ExpectedValues(
                bitrate=470_588.23529411765,
                sync_jump_width=18.235294117647058,
                sample_point=81.76470588235294,
                tq=170,
                prop=107,
                phase1=31,
                phase2=31,
                sjw=31,
                prescaler=1,
            ),
        ),
        (
            TargetValues(
                bitrate=470_000,
                sync_jump_width=33.5,
                sample_point=82,
                prop=None,
                prescaler=2,
            ),
            ExpectedValues(
                bitrate=470_588.23529411765,
                sync_jump_width=17.647058823529413,
                sample_point=82.35294117647058,
                tq=85,
                prop=54,
                phase1=15,
                phase2=15,
                sjw=15,
                prescaler=2,
            ),
        ),
        (
            TargetValues(
                bitrate=666_666,
                sync_jump_width=18.33333333333333,
                sample_point=80,
                prop=None,
                prescaler=1,
            ),
            ExpectedValues(
                bitrate=666_666.6666666666,
                sync_jump_width=18.333333333333332,
                sample_point=80,
                tq=120,
                prop=71,
                phase1=24,
                phase2=24,
                sjw=22,
                prescaler=1,
            ),
        ),
        (
            TargetValues(
                bitrate=666_666,
                sync_jump_width=33,
                sample_point=80,
                prop=70,
                prescaler=1,
            ),
            ExpectedValues(
                bitrate=666_666.6666666666,
                sync_jump_width=20.0,
                sample_point=80,
                tq=120,
                prop=70,
                phase1=25,
                phase2=24,
                sjw=24,
                prescaler=1,
            ),
        ),
        (
            TargetValues(
                bitrate=666_666,
                sync_jump_width=0,
                sample_point=80,
                prop=70,
                prescaler=1,
            ),
            ExpectedValues(
                bitrate=666_666.6666666666,
                sync_jump_width=0.8333333333333334,
                sample_point=80,
                tq=120,
                prop=70,
                phase1=25,
                phase2=24,
                sjw=1,
                prescaler=1,
            ),
        ),
        (
            TargetValues(
                bitrate=666_666,
                sync_jump_width=0,
                sample_point=80,
                prop=70,
                prescaler=2,
            ),
            ExpectedValues(
                bitrate=666_666.6666666666,
                sync_jump_width=1.6666666666666667,
                sample_point=80,
                tq=60,
                prop=35,
                phase1=12,
                phase2=12,
                sjw=1,
                prescaler=2,
            ),
        ),
        (
            TargetValues(
                bitrate=111_111,
                sync_jump_width=33.3,
                sample_point=80,
                prop=70,
                prescaler=24,
            ),
            ExpectedValues(
                bitrate=111_111.11111111111,
                sync_jump_width=20.0,
                sample_point=80.0,
                tq=30,
                prop=3,
                phase1=20,
                phase2=6,
                sjw=6,
                prescaler=24,
            ),
        ),
        (
            TargetValues(
                bitrate=7_300,
                sync_jump_width=12.3,
                sample_point=75,
                prop=2_000,
                prescaler=90,
            ),
            ExpectedValues(
                bitrate=7_285.974499089253,
                sync_jump_width=12.295081967213115,
                sample_point=75.40983606557377,
                tq=122,
                prop=22,
                phase1=69,
                phase2=30,
                sjw=15,
                prescaler=90,
            ),
        ),
        (
            TargetValues(
                bitrate=1_666_666,
                sync_jump_width=12.3,
                sample_point=75,
                prop=40,
                prescaler=2,
            ),
            ExpectedValues(
                bitrate=1_666_666.6666666667,
                sync_jump_width=4.166666666666666,
                sample_point=75.0,
                tq=24,
                prop=16,
                phase1=1,
                phase2=6,
                sjw=1,
                prescaler=2,
            ),
        ),
    ],
)
def test_calc_busparamstq(target, expected):
    """Test calculation of BusParamsTq"""
    clk_freq = 80_000_000

    param = canlib.busparams.calc_busparamstq(
        target_bitrate=target.bitrate,
        target_sync_jump_width=target.sync_jump_width,
        target_sample_point=target.sample_point,
        clk_freq=clk_freq,
        target_prop_tq=target.prop,
        prescaler=target.prescaler,
    )
    assert param.bitrate(clk_freq) == expected.bitrate
    assert param.sample_point() == expected.sample_point
    assert param.sync_jump_width() == expected.sync_jump_width
    assert param.tq == expected.tq
    assert param.prop == expected.prop
    assert param.phase1 == expected.phase1
    assert param.phase2 == expected.phase2
    assert param.sjw == expected.sjw
    assert param.prescaler == expected.prescaler


def test_df_calc_nominal():
    """Test tolerance calculations using only nominal values"""
    params_n = canlib.busparams.BusParamsTq(
        tq=160, phase1=21, phase2=21, sjw=21, prescaler=1, prop=117
    )

    tolerance = canlib.busparams.calc_tolerance(nominal=params_n, data=None)
    assert tolerance.df1 == 13125
    assert tolerance.df2 == 10199
    assert tolerance.df3 is None
    assert tolerance.df4 is None
    assert tolerance.df5 is None


def test_df_calc():
    """Test tolerance calculations"""
    params_n = canlib.busparams.BusParamsTq(
        tq=160, phase1=21, phase2=21, sjw=21, prescaler=1, prop=117
    )

    params_d = canlib.busparams.BusParamsTq(
        tq=80,
        phase1=40,
        phase2=39,
        sjw=39,
        prescaler=1,
    )
    tolerance = canlib.busparams.calc_tolerance(nominal=params_n, data=params_d)
    assert tolerance.df1 == 13125
    assert tolerance.df2 == 10199
    assert tolerance.df3 == 48750
    assert tolerance.df4 == 13453
    assert tolerance.df5 == 59271


@pytest.mark.feature(features.canfd)
def test_to_BusParamsTq(channel_no):
    """Test converting bus parameters using to_BusParamsTq()"""

    ch = canlib.openChannel(channel_no, canlib.Open.CAN_FD)
    if isinstance(ch.bphelper, canlib.channel.BusParamHelperLegacy):
        pytest.skip()
    clk_freq = ch.channel_data.clock_info.frequency()
    # Bitrates are 500Kbit/s and 1Mbit/s
    bpA = canlib.busparams.BusParamsTq(tq=80, phase1=16, phase2=16, sjw=16, prescaler=2, prop=47)
    bpD = canlib.busparams.BusParamsTq(tq=40, phase1=31, phase2=8, sjw=8, prescaler=2)

    ch.set_bus_params_tq(bpA, bpD)
    bsA = canlib.busparams.BitrateSetting(*ch.getBusParams())
    bsD = canlib.busparams.BitrateSetting(*ch.getBusParamsFd())
    assert canlib.busparams.to_BusParamsTq(clk_freq, bsA, prescaler=2, data=False) == bpA
    assert canlib.busparams.to_BusParamsTq(clk_freq, bsD, prescaler=2, data=True) == bpD
    ch.close()


@pytest.mark.feature(features.canfd)
def test_to_BitrateSetting(channel_no):
    """Test converting bus parameters using to_BitrateSetting()"""
    ch = canlib.openChannel(channel_no, canlib.Open.CAN_FD)
    if isinstance(ch.bphelper, canlib.channel.BusParamHelperLegacy):
        pytest.skip()
    clk_freq = ch.channel_data.clock_info.frequency()
    bsA = canlib.busparams.BitrateSetting(freq=500000.0, tseg1=63, tseg2=16, sjw=16)
    bsD = canlib.busparams.BitrateSetting(freq=1000000.0, tseg1=31, tseg2=8, sjw=8)
    ch.setBusParams(bsA.freq, bsA.tseg1, bsA.tseg2, bsA.sjw)
    ch.setBusParamsFd(bsD.freq, bsD.tseg1, bsD.tseg2, bsD.sjw)
    assert canlib.busparams.to_BitrateSetting(clk_freq, ch.get_bus_params_tq()[0]) == bsA
    assert canlib.busparams.to_BitrateSetting(clk_freq, ch.get_bus_params_tq()[1]) == bsD
    ch.close()


@pytest.mark.feature(features.canfd)
def test_predefined_bitrates(channel_no):
    """ Test using predefined bitrates on channels supporting Tq"""
    ch = canlib.openChannel(channel_no, canlib.Open.CAN_FD)
    if isinstance(ch.bphelper, canlib.channel.BusParamHelperLegacy):
        pytest.skip()
    freq_a = canlib.canFD_BITRATE_500K_80P
    freq_d = canlib.canFD_BITRATE_1M_80P
    bpA, bpD = ch.bphelper.bitrate_to_BusParamsTq(freq_a=freq_a, freq_d=freq_d)
    ch.setBusParams(freq_a)
    ch.setBusParamsFd(freq_d)
    bp1, bp2 = ch.get_bus_params_tq()
    clk = ch.channel_data.clock_info.frequency()
    assert bp1.bitrate(clk) == bpA.bitrate(clk)
    assert bp1.sample_point() == bpA.sample_point()
    assert bp1.sync_jump_width() == bpA.sync_jump_width()
    assert bp2.bitrate(clk) == bpD.bitrate(clk)
    assert bp2.sample_point() == bpD.sample_point()
    assert bp2.sync_jump_width() == bpD.sync_jump_width()
    ch.close()


@pytest.mark.feature(features.canfd)
def test_BusParamHelperLegacy_tq_err(channel_no):
    """Test error message when trying to use tq functions on old devices"""
    ch = canlib.openChannel(channel_no, canlib.Open.CAN_FD)
    ch.bphelper = canlib.channel.BusParamHelperLegacy(ch)
    bpA = canlib.busparams.BusParamsTq(tq=80, phase1=16, phase2=16, sjw=16, prescaler=2, prop=47)
    bpD = canlib.busparams.BusParamsTq(tq=40, phase1=31, phase2=8, sjw=8, prescaler=2)
    with pytest.raises(TypeError):
        ch.set_bus_params_tq(bpA, bpD)
    with pytest.raises(TypeError):
        ch.get_bus_params_tq()

    ch.close()


def test_BusParamHelperLegacy_set_and_get(channel_no):
    ch = canlib.openChannel(channel_no, canlib.Open.CAN_FD)
    ch.bphelper = canlib.channel.BusParamHelperLegacy(ch)
    expectedA = (500000, 63, 16, 16)
    expectedD = (1000000, 31, 8, 8)
    ch.setBusParams(canlib.canFD_BITRATE_500K_80P)
    ch.setBusParamsFd(canlib.canFD_BITRATE_1M_80P)
    (freq_a, tseg1_a, tseg2_a, sjw_a) = (
        ch.getBusParams()[0],
        ch.getBusParams()[1],
        ch.getBusParams()[2],
        ch.getBusParams()[3],
    )
    assert (freq_a, tseg1_a, tseg2_a, sjw_a) == expectedA
    assert ch.getBusParamsFd() == expectedD
    ch.close()
