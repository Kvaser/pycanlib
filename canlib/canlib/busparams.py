"""A set of helper functions to the new busparam API added in CANlib v5.34.

    .. versionadded:: 1.16

"""

import collections

SI_PREFIXES = {
    24: 'Y',
    21: 'Z',
    18: 'E',
    15: 'P',
    12: 'T',
    9: 'G',
    6: 'M',
    3: 'k',
    0: '',
    -3: 'm',
    -6: 'u',
    -9: 'n',
    -12: 'p',
    -15: 'f',
    -18: 'a',
    -21: 'z',
    -24: 'y',
}


def calc_bitrate(target_bitrate, clk_freq):
    """Calculate nearest available bitrate

    Args:
        target_bitrate (`int`): Wanted bitrate (bit/s)
        clk_freq (`int`): Device clock frequency (Hz)

    Returns:
        The returned tuple is a ``(bitrate, tq)`` named tuple of:

        #. ``bitrate`` (`int`): Available bitrate, could be a rounded value (bit/s)
        #. ``tq`` (`int`): Number of time quanta in one bit

    .. versionadded:: 1.16

    """
    tq = round(clk_freq / target_bitrate)
    # Minimum tq is 3 (sync_seg + phase1 + phase2)
    if tq < 3:
        tq = 3
    bitrate = clk_freq / tq

    Bitrate = collections.namedtuple('Bitrate', 'bitrate tq')
    return Bitrate(bitrate=bitrate, tq=tq)


def calc_busparamstq(
    target_bitrate,
    target_sample_point,
    target_sync_jump_width,
    clk_freq,
    target_prop_tq=None,
    prescaler=1,
):
    """Calculate closest matching busparameters.

    The device clock frequency, `clk_freq`, can be obtained via
    `ClockInfo.frequency()`:

        >>> chd = canlib.ChannelData(channel_number=0)
        >>> clock_info = chd.clock_info
        >>> clock_info.frequency()
        80000000.0

    Now call `calc_busparamstq` with target values, and a `BusParamsTq`
    object will be returned:

        >>> params = calc_busparamstq(
        ... target_bitrate=470_000,
        ... target_sample_point=82,
        ... target_sync_jump_width=15.3,
        ... clk_freq=clock_info.frequency())
        >>> params
        BusParamsTq(tq=170, prop=107, phase1=31, phase2=31, sjw=26, prescaler=1)

    A target number of time quanta in the propagation segment can also be specified
    by the user.

    The returned BusParamsTq may not be valid on all devices. If
    `Error.NOT_IMPLEMENTED <canlib.canlib.Error.NOT_IMPLEMENTED>` is encountered
    when trying to set the bitrate with the returned BusParamsTq, provide a
    prescaler argument higher than one and retry. This will lower the total number
    of time quanta in the bit and thus make the BusParamsTq valid.

    Example:

        >>> params = calc_busparamstq(
        ... target_bitrate=470_000,
        ... target_sample_point=82,
        ... target_sync_jump_width=15.3,
        ... clk_freq=clock_info.frequency(),
        ... target_prop_tq=50,
        ... prescaler=2)
        >>> params
        BusParamsTq(tq=85, prop=25, phase1=44, phase2=15, sjw=13, prescaler=2)

    Note:
        - Minimum sjw returned is 1, maximum sjw is min(phase1, phase2).

    Args:
        target_bitrate (`float`): Wanted bitrate (bit/s)
        target_sample_point (`float`): Wanted sample point in percentage (0-100)
        target_sync_jump_width (`float`): Wanted sync jump width in percentage (0-100)
        clk_freq (`float`): Device clock frequency (Hz)
        target_prop_tq (`int`, Optional): Wanted propagation segment (time quanta)
        prescaler (`int`, Optional): Wanted prescaler (at most 2 for CAN FD)

    Returns:
        `BusParamsTq`: Calculated bus parameters

    .. versionadded:: 1.16

    .. versionchanged:: 1.17

    """
    _, tq = calc_bitrate(target_bitrate * prescaler, clk_freq)
    _, phase2 = calc_sample_point(tq, target_sample_point)

    if target_prop_tq is None:
        phase1 = phase2
    else:
        scaled_target_prop = round(target_prop_tq / prescaler)
        phase1 = calc_phase_seg1(tq, scaled_target_prop, phase2)

    prop = calc_prop_seg(tq, phase1, phase2)
    sjw, _ = calc_sjw(tq, target_sync_jump_width)

    if sjw > min(phase1, phase2):
        sjw = min(phase1, phase2)

    return BusParamsTq(
        tq=tq,
        prop=prop,
        phase1=phase1,
        phase2=phase2,
        sjw=sjw,
        prescaler=prescaler,
    )


def calc_phase_seg1(tq, prop, phase2, sync_tq=1):
    """Calculate phase segment 1"""
    phase1 = tq - prop - phase2 - sync_tq
    if phase1 < 1:
        return 1
    return tq - prop - phase2 - sync_tq


def calc_prop_seg(tq, phase1, phase2, sync_tq=1):
    """Calculate propagation segment"""
    return tq - phase2 - phase1 - sync_tq


def calc_sample_point(tq, target_sample_point):
    """Calculate actual sample_point and phase segment 2

    tq (`int`): Total number of quanta in one bit
    target_sample_point (`float`): Wanted sample point in percentage (0-100)

    Returns:
        named tuple(sample_point, phase2)

    phase2: Number of time quanta in phase segment 2
    sample_point: Sample point in percentage

    .. versionadded:: 1.16

    """
    phase2 = tq - (round((target_sample_point / 100) * tq))
    sample_point = ((tq - phase2) / tq) * 100

    SamplePoint = collections.namedtuple('SamplePoint', 'sample_point phase2')
    return SamplePoint(sample_point=sample_point, phase2=phase2)


def calc_sjw(tq, target_sync_jump_width):
    """Calculate sync jump width

    tq: Number of time quanta in one bit
    target_sync_jump_width: Wanted sync jump width, 0-100 (%)

    Note: Minimum sjw_tq returned is 1.

    Returns:
        The returned named tuple is a ``(sjw_tq, sync_jump_width)`` consisting of:

        #. ``sjw_tq`` (`int`): Size of sync jump width in number of time quanta,
        #. ``sync_jump_width`` (`number`): Size of sync jump width in percentage (%))

    .. versionadded:: 1.16

    """
    sjw_tq = round((target_sync_jump_width / 100) * tq)
    if sjw_tq < 1:
        sjw_tq = 1
    sync_jump_width = round(sjw_tq / tq * 100)

    Sjw = collections.namedtuple('Sjw', 'sjw_tq sync_jump_width')
    return Sjw(sjw_tq=sjw_tq, sync_jump_width=sync_jump_width)


def to_BusParamsTq(clk_freq, bus_param, prescaler=1, data=False):
    """Convert `BitrateSetting` or `tuple` to `BusParamsTq`.

    The device clock frequency, `clk_freq`, can be obtained via
    `ClockInfo.frequency()`:

        >>> chd = canlib.ChannelData(channel_number=0)
        >>> clock_info = chd.clock_info
        >>> clock_info.frequency()
        80000000.0

    Args:
        clk_freq (`float`): Clock frequency of device.

        bus_param (`BitrateSetting` or `tuple`): `BitrateSetting` object or
        (freq, tseg1, tseg2, sjw) `tuple` to convert.

        prescaler (`int`): The prescaler to use in the created `BusParamsTq`
        object.

        data (`bool`): Set to True if the resulting `BusParamsTq` should be
        used for CAN FD data bitrate parameters.

    Returns:
        `BusParamsTq` object with equivalent settings as the input argument.

    .. versionadded:: 1.17

    """
    if bus_param is None:
        return None

    if isinstance(bus_param, tuple):
        bs = BitrateSetting(*bus_param)
    elif isinstance(bus_param, BitrateSetting):
        bs = bus_param
    else:
        err_msg = "bus_param must be a BitrateSetting or a (freq, tseg1, tseg2, sjw) tuple."
        raise TypeError(err_msg)

    target_sample_point = 100 * (1 + bs.tseg1) / (1 + bs.tseg1 + bs.tseg2)
    target_sjw = 100 * bs.sjw / (1 + bs.tseg1 + bs.tseg2)
    bptq = calc_busparamstq(round(bs.freq), target_sample_point, target_sjw, clk_freq)

    # calc_busparamstq uses prescaler 1, so needs conversion
    if prescaler != 1:
        bptq.prescaler = prescaler
        bptq.tq = bptq.tq // prescaler
        bptq.phase1 = bptq.phase1 // prescaler
        bptq.phase2 = bptq.phase2 // prescaler
        bptq.sjw = bptq.sjw // prescaler
        bptq.prop = bptq.prop // prescaler
        assert bptq.tq == bptq.prop + bptq.phase1 + bptq.phase2 + 1

    # if bptq.sjw < 1:
    #     bptq.sjw = 1

    if data is True:
        bptq.phase1 += bptq.prop
        bptq.prop = 0

    return bptq


def to_BitrateSetting(clk_freq, bus_param):
    """Convert `BusParamsTq` to `BitrateSetting`.

    The device clock frequency, `clk_freq`, can be obtained via
    `ClockInfo.frequency()`:

        >>> chd = canlib.ChannelData(channel_number=0)
        >>> clock_info = chd.clock_info
        >>> clock_info.frequency()
        80000000.0

    Args:
        clk_freq (`float`): Clock frequency of device.

        bus_param (`BusParamsTq`): `BusParamsTq` object to convert.

    Returns:
        `BitrateSetting` object with equivalent settings as the input argument.

    .. versionadded:: 1.17

    """
    if bus_param is None:
        return None

    if not isinstance(bus_param, BusParamsTq):
        raise TypeError("bus_param must be a BusParamsTq object.")

    bitrate = bus_param.bitrate(clk_freq)
    tseg1 = bus_param.prop + bus_param.phase1
    return BitrateSetting(bitrate, tseg1, bus_param.phase2, bus_param.sjw)


class ClockInfo:
    """Information about clock a oscillator

    The clock frequency is set in the form:

        frequency = numerator / denominator * 10 ** power_of_ten +/- accuracy

    .. versionadded:: 1.16

    """

    @classmethod
    def from_list(cls, args):
        """Create a `ClockInfo` object from a versioned list of values.

        The first number in the list is the version number for the list and
        must be 1. See the `kvClockInfo` structure in CANlib for more
        information.

        Args:
            args (`list` (version (`int`), ...)): where version must be 1.

        Returns:
            `ClockInfo`

        """
        version = args[0]
        if version == 1:
            return ClockInfo(
                numerator=args[1],
                denominator=args[2],
                power_of_ten=args[3],
                accuracy=args[4],
            )
        else:
            raise ValueError(
                f"Clock info version '{version}' is unknown, perhaps update canlib?"
            )

    def __init__(self, numerator, denominator, power_of_ten, accuracy):
        self.numerator = numerator
        self.denominator = denominator
        self.power_of_ten = power_of_ten
        self.accuracy = accuracy

    def __eq__(self, other):
        if not isinstance(other, ClockInfo):
            return NotImplemented
        if self.accuracy != other.accuracy:
            return False
        if self.frequency() != other.frequency():
            return False
        return True

    def __repr__(self):
        txt = (
            f"ClockInfo(numerator={self.numerator}, denominator={self.denominator}, "
            f"power_of_ten={self.power_of_ten}, accuracy={self.accuracy})"
        )
        return txt

    def __str__(self):
        frequency = self.frequency()
        if self.power_of_ten in SI_PREFIXES:
            frequency = frequency / 10 ** self.power_of_ten
            si_prefix = SI_PREFIXES[self.power_of_ten]
        else:
            si_prefix = ""
        txt = self.__repr__() + f", (frequency: {frequency} {si_prefix}Hz)"
        return txt

    def frequency(self):
        """Returns an approximation of the clock frequency as a float."""
        return self.numerator / self.denominator * 10 ** self.power_of_ten


class BusParamTqLimits:
    """Hold min and max values for both arbitration and data phase.

    The ``tq`` field is ignored during validation since
    `.ChannelData.bus_param_limits` always returns zero for this field.

    If ``prop`` is zero for both ``min`` and ``max`` values, the ``phase1``
    limit applies to (``phase1`` + ``prop``). This is used when a device
    does not distinguish between phase segment one and the propagation
    segment.

    Example usage:

        >>> ch = canlib.openChannel(channel=0)
        >>> limits = canlib.ChannelData(channel_number=0).bus_param_limits
        >>> limits.arbitration_max._asdict()
        {'tq': 0, 'phase1': 32, 'phase2': 32, 'sjw': 32, 'prescaler': 1024, 'prop': 64}
        >>> bp_tq = canlib.busparams.BusParamsTq(tq=121, phase1=100, phase2=10, sjw=10,
        ... prescaler=10, prop=10)
        >>> limits.validate(bp_tq)
        ValueError: The following does not match:
          Arbitration phase1: 1 <= 100 <= 32

    NOTE: This class is preliminary and may change!

    .. versionadded:: 1.20

    """
    def __init__(self, arbitration_min, arbitration_max, data_min, data_max):
        self.arbitration_min = arbitration_min
        self.arbitration_max = arbitration_max
        self.data_min = data_min
        self.data_max = data_max

    def __str__(self):
        txt = (f"BusParamTqLimits(arbitration_min={self.arbitration_min._asdict()},"
               f" arbitration_max={self.arbitration_max._asdict()},"
               f" data_min={self.data_min._asdict()}, data_max={self.data_max._asdict()}")
        return txt

    def _validation_error_text(self, value, minimum, maximum):
        """Validate that minimum <= value <= maximum

        Returns empty string if validation suceeds, otherwise returns a string
        with the comparison done.

        """
        if minimum <= value <= maximum:
            message = ""
        else:
            message = f"{minimum} <= {value} <= {maximum}"
        return message

    def validate(self, bus_param, data_param=None):
        """Validates busparameters for arbitration and data

        Raises a `ValueError` if busparameters for arbritation and data is not
        within current limits. The failed validation is provided as an explanation::

            ValueError: The following does not match:
              Arbitration phase1: 11 <= 1 <= 21

        """
        error_message = ""
        params = ["phase1", "phase2", "sjw", "prescaler", "prop"]
        if self.arbitration_min.prop == self.arbitration_max.prop == 0:
            is_prop_limit_zero = True
        else:
            is_prop_limit_zero = False
        if bus_param is not None:
            for attribute in params:
                value = getattr(bus_param, attribute)
                if is_prop_limit_zero and attribute == "phase1":
                    value += bus_param.prop
                if is_prop_limit_zero and attribute == "prop":
                    continue

                message = self._validation_error_text(
                    value=value,
                    minimum=getattr(self.arbitration_min, attribute),
                    maximum=getattr(self.arbitration_max, attribute),
                )
                if message:
                    error_message += f"\n  Arbitration {attribute}: {message}"
        if self.data_min.prop == self.data_max.prop == 0:
            is_prop_limit_zero = True
        else:
            is_prop_limit_zero = False
        if data_param is not None:
            for attribute in params:
                value = getattr(data_param, attribute)
                if is_prop_limit_zero and attribute == "phase1":
                    value += data_param.prop
                if is_prop_limit_zero and attribute == "prop":
                    continue
                message = self._validation_error_text(
                    value=value,
                    minimum=getattr(self.data_min, attribute),
                    maximum=getattr(self.data_max, attribute),
                )
                if message:
                    error_message += f"\n  Data {attribute}: {message}"
        if error_message:
            raise ValueError("The following does not match:" + error_message)


class BusParamsTq:
    """Holds parameters for busparameters in number of time quanta.

    If you don't want to specify the busparameters in time quanta directly,
    you may use `calc_busparamstq` which returns an object of this class.

        >>> params = calc_busparamstq(
        ... target_bitrate=470_000,
        ... target_sample_point=82,
        ... target_sync_jump_width=33.5,
        ... clk_freq=clk_freq)
        >>> params
        BusParamsTq(tq=170, prop=107, phase1=31, phase2=31, sjw=57, prescaler=1)

    You may now query for the actual Sample Point and Sync Jump Width expressed
    as percentages of total bit time quanta:

        >>> params.sample_point()
        81.76470588235294

        >>> params.sync_jump_width()
        33.52941176470588


    If you supply the clock frequency, you may also calculate the corresponding bitrate:

        >>> params.bitrate(clk_freq=80_000_000)
        470588.23529411765

    Args:
        tq (`int`): Number of time quanta in one bit.
        phase1 (`int`): Number of time quanta in Phase Segment 1.
        phase2 (`int`): Number of time quanta in Phase Segment 2.
        sjw (`int`): Number of time quanta in Sync Jump Width.
        prescaler (`int`): Prescaler value (1-2 to enable auto in CAN FD)
        prop (`int`, optional): Number of time quanta in Propagation Segment.


    .. versionadded:: 1.16

    """

    def __init__(self, tq, phase1, phase2, sjw, prescaler=1, prop=None):
        self.sync = 1
        if prop is None:
            self.prop = tq - phase1 - phase2 - self.sync
        else:
            self.prop = prop
        if tq != self.sync + self.prop + phase1 + phase2:
            raise ValueError(
                f"Total number of time quanta does not match: {tq}(tq) !="
                f" {self.sync}(sync) + {self.prop}(prop) + {phase1}(phase1) + {phase2}(phase2)"
            )
        self.tq = tq
        self.phase1 = phase1
        self.phase2 = phase2
        self.sjw = sjw
        self.prescaler = prescaler

    def __eq__(self, other):
        if not isinstance(other, BusParamsTq):
            return NotImplemented
        if self.tq != other.tq:
            return False
        if self.phase1 != other.phase1:
            return False
        if self.phase2 != other.phase2:
            return False
        if self.sjw != other.sjw:
            return False
        if self.prescaler != other.prescaler:
            return False
        if self.prop != other.prop:
            return False
        return True

    def __str__(self):
        txt = (
            f"BusParamsTq(tq={self.tq}, prop={self.prop}, phase1={self.phase1},"
            f" phase2={self.phase2}, sjw={self.sjw}, prescaler={self.prescaler})"
        )
        return txt

    def bitrate(self, clk_freq):
        """Return bitrate assuming the given clock frequency

        Args:
            clk_freq (`int`): Clock frequency (in Hz)
        """
        return clk_freq / (self.tq * self.prescaler)

    def sample_point(self):
        """Return sample point in percentage."""
        return ((self.tq - self.phase2) / self.tq) * 100

    def sample_point_ns(self, clk_freq):
        """Return sample point in ns.

        .. versionadded:: 1.17

        """
        return ((self.prescaler * (self.tq - self.phase2)) / clk_freq) * 1_000_000_000

    def sync_jump_width(self):
        """Return sync jump width (SJW) in percentage."""
        return self.sjw / self.tq * 100


class BitrateSetting:
    """Class that holds bitrate setting.

    Args:
        freq: Bitrate in bit/s.
        tseg1: Number of quanta from (but not including) the Sync Segment to \
            the sampling point.
        tseg2: Number of quanta from the sampling point to the end of the bit.
        sjw: The Synchronization Jump Width.
        nosamp: The number of sampling points, only 1 is supported.
        syncMode: Unsupported and ignored.

    .. versionadded:: 1.17
    """

    def __init__(self, freq, tseg1, tseg2, sjw, nosamp=1, syncMode=0):
        self.freq = freq
        self.tseg1 = tseg1
        self.tseg2 = tseg2
        self.sjw = sjw
        self.nosamp = nosamp
        self.syncMode = syncMode

    def __eq__(self, other):
        if self.freq != other.freq:
            return False
        if self.tseg1 != other.tseg1:
            return False
        if self.tseg2 != other.tseg2:
            return False
        if self.sjw != other.sjw:
            return False
        if self.nosamp != other.nosamp:
            return False
        if self.syncMode != other.syncMode:
            return False
        return True

    # required in Python 2
    def __ne__(self, other):
        return not self == other

    def __str__(self):
        txt = f"freq    : {self.freq:8}\n"
        txt += f"tseg1   : {self.tseg1:8}\n"
        txt += f"tseg2   : {self.tseg2:8}\n"
        txt += f"sjw     : {self.sjw:8}\n"
        txt += f"nosamp  : {self.nosamp:8}\n"
        txt += f"syncMode: {self.syncMode:8}\n"
        return txt

    @classmethod
    def from_predefined(cls, bitrate):
        """Create a BitrateSetting object using one of the `~canlib.canlib.Bitrate` or
        `~canlib.canlib.BitrateFD` enumerations.

        """
        return cls(freq=bitrate, tseg1=0, tseg2=0, sjw=0, nosamp=0, syncMode=0)


def calc_tolerance(nominal, data=None):
    """Calculate tolerance with the given `BusParamsTq`.

    Args:
        nominal (`BusParamsTq`): Nominal bus parameters
        data (`BusParamsTq`, optional): Bus parameters for data phase (in CAN FD)

    Returns:
        `namedtuple`: (df1, df2, df3, df4, df5)

    .. versionadded:: 1.16

    """
    df1 = nominal.sjw / (2 * 10 * nominal.tq)
    df1 = round((df1 * 2) * 1000000)

    min_Tphase_seg = min(nominal.phase1, nominal.phase2)
    df2 = min_Tphase_seg / ((13 * nominal.tq) - nominal.phase2)
    df2 = round(df2 * 1000000)

    if data is None:
        df3 = None
        df4 = None
        df5 = None
    else:
        df3 = data.sjw / (10 * data.tq)
        df3 = round(df3 * 1000000)

        d_n_ratio = data.prescaler / nominal.prescaler
        df4 = min_Tphase_seg / (6 * data.tq - data.phase2 * d_n_ratio + 7 * nominal.tq)
        df4 = round(df4 * 1000000)

        n_d_ratio = nominal.prescaler / data.prescaler
        df5 = (data.sjw - max(0, n_d_ratio - 1)) / (
            (2 * nominal.tq - nominal.phase2) * n_d_ratio + data.phase2 + 4 * data.tq
        )
        df5 = round(df5 * 1000000)

    Tolerance = collections.namedtuple('Tolerance', 'df1 df2 df3 df4 df5')
    return Tolerance(df1=df1, df2=df2, df3=df3, df4=df4, df5=df5)
