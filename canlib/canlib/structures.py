import ctypes as ct

from .busparams import BusParamsTq


class CanBusParamsTq(ct.Structure):
    """Holds bus parameters expressed as number of time quanta

    Attributes:
        tq (`int`): Total bit length, in number of time quanta.
        phase1 (`int`): Phase segment 1, in number of time quanta.
        phase2 (`int`): Phase segment 2, in number of time quanta.
        sjw (`int`): Sync Jump Width, in number of time quanta.
        prop (`int`): Propagation segment, in number of time quanta.
        prescaler (`int`): Prescaler, should typically be 1 or 2.

    .. versionadded:: 1.16

    """

    @classmethod
    def _frombusparamstq(cls, busparamstq):
        return cls(
            tq=busparamstq.tq,
            phase1=busparamstq.phase1,
            phase2=busparamstq.phase2,
            sjw=busparamstq.sjw,
            prescaler=busparamstq.prescaler,
            prop=busparamstq.prop,
        )

    _fields_ = [
        ('tq', ct.c_int),
        ('phase1', ct.c_int),
        ('phase2', ct.c_int),
        ('sjw', ct.c_int),
        ('prop', ct.c_int),
        ('prescaler', ct.c_int),
    ]

    def _tobusparamstq(self):
        return BusParamsTq(
            tq=self.tq,
            phase1=self.phase1,
            phase2=self.phase2,
            sjw=self.sjw,
            prescaler=self.prescaler,
            prop=self.prop,
        )

    def _asdict(self):
        return {
            'tq': self.tq,
            'phase1': self.phase1,
            'phase2': self.phase2,
            'sjw': self.sjw,
            'prescaler': self.prescaler,
            'prop': self.prop,
        }


class CanBusStatistics(ct.Structure):
    """Result from reading bus statistics using `canlib.canlib.Channel.get_bus_statistics`.

    Attributes:
        busLoad (`int`): The bus load, expressed as an integer in the interval
            0 - 10000 representing 0.00% - 100.00% bus load.
        errFrame (`int`): Number of error frames.
        extData (`int`): Number of received extended (29-bit identifiers) data frames.
        extRemote (`int`): Number of received extended (29-bit identifiers) remote frames.
        overruns (`int`): The number of overruns detected by the hardware, firmware or driver.
        stdData (`int`): Number of received standard (11-bit identifiers) data frames.
        stdRemote (`int`): Number of received standard (11-bit identifiers) remote frames.

    """

    _fields_ = [
        ('stdData', ct.c_ulong),
        ('stdRemote', ct.c_ulong),
        ('extData', ct.c_ulong),
        ('extRemote', ct.c_ulong),
        ('errFrame', ct.c_ulong),
        ('busLoad', ct.c_ulong),
        ('overruns', ct.c_ulong),
    ]


class CanBusParamLimits(ct.Structure):
    _fields_ = [
        ('version', ct.c_int),  # Version of struct, currently 2
        ('arbitration_min', CanBusParamsTq),
        ('arbitration_max', CanBusParamsTq),
        ('data_min', CanBusParamsTq),
        ('data_max', CanBusParamsTq),
    ]


class kvTimeDomainData(ct.Structure):
    _fields_ = [
        ('nMagiSyncGroups', ct.c_int),
        ('nMagiSyncedMembers', ct.c_int),
        ('nNonMagiSyncCards', ct.c_int),
        ('nNonMagiSyncedMembers', ct.c_int),
    ]