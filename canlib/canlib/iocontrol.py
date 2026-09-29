import sys
import ctypes as ct
from collections import namedtuple

from .enums import BusTypeGroup, IOControlItem
from .wrapper import dll

Property = dict
Function = namedtuple('Function', 'item arg ret doc')


def _get_tx_interval(ioc):
    return ioc.raw(
        item=IOControlItem.TX_INTERVAL,
        value=0xFFFFFFFF,
        ctype=ct.c_uint32,
    )


# In Python 2, xrange requires its arguments to fit into a C long (sys.maxint, which is 32bit on 64bit windows)
# https://stackoverflow.com/questions/42256542/python-overflow-error-int-too-large-to-convert-to-c-long
# In 32 bit Python 3.6, using range(0, 4294967295),  we got "OverflowError: Python int too large to convert to C ssize_t"
try:
    _tx_interval_range = range(0, 0xFFFFFFFF)
except OverflowError:
    _tx_interval_range = range(0, sys.maxint)


# wintypes does not exist on Linux
try:
    _c_win_handle = ct.wintypes.HANDLE
except AttributeError:
    _c_win_handle = ct.c_int

ATTRIBUTES = {
    # properties
    'timer_scale': Property(
        getitem=IOControlItem.GET_TIMER_SCALE,
        setitem=IOControlItem.SET_TIMER_SCALE,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the time-stamp clock resolution in microseconds."
                " Used e.g. in `.Channel.read()`. Default is 1000, i.e. 1 ms.",
    ),
    'txack': Property(
        getitem=IOControlItem.GET_TXACK,
        setitem=IOControlItem.SET_TXACK,
        ctype=ct.c_uint32,
        ptype=int,
        values=(0, 1, 2),
        __doc__="0 for Transmit Acknowledges off, 1 for Transmit Acknowledges on, and 2 for Transmit Acknowledges off, even for the driver's internal usage (this will break parts of the library).",
    ),
    'rx_buffer_level': Property(
        getitem=IOControlItem.GET_RX_BUFFER_LEVEL,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the approximate receive queue level. Read-only.",
    ),
    'tx_buffer_level': Property(
        getitem=IOControlItem.GET_TX_BUFFER_LEVEL,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the approximate transmit queue level. Read-only.",
    ),
    'txrq': Property(
        setitem=IOControlItem.SET_TXRQ,
        ctype=ct.c_uint32,
        ptype=bool,
        __doc__="A `bool` for whether Transmit Requests are turned on. Write-only.",
    ),
    'eventhandle': Property(  # winonly
        getitem=IOControlItem.GET_EVENTHANDLE,
        ctype=_c_win_handle,
        ptype=int,
        __doc__="An `int` with the windows event handle. Not implemented in Linux. Read-only.",
    ),
    'driverhandle': Property(  # winonly
        getitem=IOControlItem.GET_DRIVERHANDLE,
        ctype=_c_win_handle,
        ptype=int,
        __doc__="The windows handle related to the CANlib handle. Not implemented in Linux. Read-only.",
    ),
    'report_access_errors': Property(
        getitem=IOControlItem.GET_REPORT_ACCESS_ERRORS,
        setitem=IOControlItem.SET_REPORT_ACCESS_ERRORS,
        ctype=ct.c_uint32,
        ptype=bool,
        __doc__="A `bool` for whether Access Reporting is turned on. Default is `False` (off).",
    ),
    # 'user_ioport': Property(  # winonly
    #     getitem=IOControlItem.GET_USER_IOPORT,
    #     setitem=IOControlItem.SET_USER_IOPORT,
    #     ctype=UserIOPortData,
    #     ptype=UserIOPortData,
    # ),
    'rx_queue_size': Property(  # winonly
        setitem=IOControlItem.SET_RX_QUEUE_SIZE,
        ctype=ct.c_uint,
        ptype=int,
        __doc__="An `int` with the size of the receive buffer. Can only be used off-bus. Not implemented in Linux. Write-only.",
    ),
    'buson_time_auto_reset': Property(
        setitem=IOControlItem.SET_BUSON_TIME_AUTO_RESET,
        ctype=ct.c_uint32,
        ptype=bool,
        __doc__="A `bool` for whether the CAN clock is reset at bus-on. Not implemented in Linux. Write-only.",
    ),
    'local_txecho': Property(
        setitem=IOControlItem.SET_LOCAL_TXECHO,
        ctype=ct.c_uint32,
        ptype=bool,
        __doc__="A `bool` for whether local transmit echo is turned on. Write-only.",
    ),
    'error_frames_reporting': Property(  # winonly
        setitem=IOControlItem.SET_ERROR_FRAMES_REPORTING,
        ctype=ct.c_uint32,
        ptype=bool,
        __doc__="A `bool` for whether error frames are reported. Not implemented in Linux. Write-only.",
    ),
    'channel_quality': Property(  # winonly
        getitem=IOControlItem.GET_CHANNEL_QUALITY,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` between 0 and 100 (inclusively) with the quality of the channel in percent. Not implemented in Linux. Read-only.",
    ),
    'roundtrip_time': Property(  # winonly
        getitem=IOControlItem.GET_ROUNDTRIP_TIME,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the roundtrip time in milliseconds. Not implemented in Linux. Read-only.",
    ),
    'bus_type': Property(  # winonly
        getitem=IOControlItem.GET_BUS_TYPE,
        ctype=ct.c_uint32,
        ptype=BusTypeGroup,
        __doc__="A member of the `BusTypeGroup` enum. Not implemented in Linux. Read-only.",
    ),
    'devname_ascii': Property(  # winonly
        getitem=IOControlItem.GET_DEVNAME_ASCII,
        ctype=ct.c_char * 80,
        ptype=str,
        __doc__="A `str` with the current device name. Not implemented in Linux. Read-only.",
    ),
    'time_since_last_seen': Property(  # winonly
        getitem=IOControlItem.GET_TIME_SINCE_LAST_SEEN,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the time in milliseconds since the last communication occured. Not implemented in Linux. Read-only.",
    ),
    'throttle_scaled': Property(  # winonly
        getitem=IOControlItem.GET_THROTTLE_SCALED,
        setitem=IOControlItem.SET_THROTTLE_SCALED,
        ctype=ct.c_uint32,
        ptype=int,
        values=range(0, 101),
        __doc__="An `int` between 0 and 100 (inclusively) where 0 means the device is very responsive but generates more CPU load and 100 means the device is less responsive with less CPU load. Note that not all devices support setting this. Some hardware will accept this command but neglect it. Not implemented in Linux.",
    ),
    'brlimit': Property(
        setitem=IOControlItem.SET_BRLIMIT,
        ctype=ct.c_long,
        ptype=int,
        __doc__="An `int` with the hardware bitrate limit, or zero for the device's default. Write-only.",
    ),
    'tx_interval': Property(
        getfunc=_get_tx_interval,
        setitem=IOControlItem.TX_INTERVAL,
        ctype=ct.c_uint32,
        ptype=int,
        values=_tx_interval_range,
        __doc__="An `int` with the number of microseconds with the minimum CAN message transmit interval.",
    ),
    'local_txack': Property(
        setitem=IOControlItem.SET_LOCAL_TXACK,
        ctype=ct.c_uint32,
        ptype=bool,
        __doc__="A `bool` for whether local transmit acknowledge is turned on. Write-only.",
    ),

    # functions
    'prefer_ext': Function(
        IOControlItem.PREFER_EXT,
        None,
        None,
        (
            "Tells CANlib to assume `MessageFlag.EXT` when sending messages if neither `MessageFlag.EXT` or `MessageFlag.STD` is specified. Not implemented in Linux."
        ),
    ),
    'prefer_std': Function(
        IOControlItem.PREFER_STD,
        None,
        None,
        (
            "Tells CANlib to assume `MessageFlag.STD` when sending messages if neither `MessageFlag.EXT` or `MessageFlag.STD` is specified. Not implemented in Linux."
        ),
    ),
    'clear_error_counters': Function(
        IOControlItem.CLEAR_ERROR_COUNTERS,
        None,
        None,
        (
            "Tells CANlib to clear the CAN error counters. CAN error counters on device side are NOT updated. It is recommended to use `reset_overrun_count` to reset overrun status. Not implemented in Linux."
        ),
    ),
    'flush_rx_buffer': Function(
        IOControlItem.FLUSH_RX_BUFFER,
        None,
        None,
        ("Discard the current contents of the RX queue."),
    ),
    'flush_tx_buffer': Function(
        IOControlItem.FLUSH_TX_BUFFER,
        None,
        None,
        ("Discard the current contents of the TX queue."),
    ),
    'connect_to_virtual_bus': Function(
        IOControlItem.CONNECT_TO_VIRTUAL_BUS,
        (int, range(0, 31), ct.c_uint32),
        None,
        "Connects the channel to the virtual bus number `value`.",
    ),
    'disconnect_from_virtual_bus': Function(
        IOControlItem.DISCONNECT_FROM_VIRTUAL_BUS,
        (int, range(0, 31), ct.c_uint32),
        None,
        "Disconnects the channel from the virtual bus number `value`.",
    ),
    'reset_overrun_count': Function(
        IOControlItem.RESET_OVERRUN_COUNT, None, None, ("Resets overrun count and flags.")
    ),
}
# # functions
# "canIOCTL_PREFER_EXT", 1, None
# "canIOCTL_PREFER_STD", 2, None
# "canIOCTL_CLEAR_ERROR_COUNTERS", 5, None
# "canIOCTL_FLUSH_RX_BUFFER", 10, None
# "canIOCTL_FLUSH_TX_BUFFER", 11, None
# "canIOCTL_CONNECT_TO_VIRTUAL_BUS", 22, in, [0-31]
# "canIOCTL_DISCONNECT_FROM_VIRTUAL_BUS", 23, in, [0-31]
# "canIOCTL_RESET_OVERRUN_COUNT", 44, None

# # NotImplemented
# "canIOCTL_SET_BYPASS_MODE", 15, NotImplemented

# # NotSupported
# "canIOCTL_GET_TREF_LIST", 39, get, [int64]:(ref, time), "not supported"

# # internal use_planka
# "canIOCTL_SET_WAKEUP", 16, internal use
# "canIOCTL_MAP_RXQUEUE", 18, internal
# "canIOCTL_GET_WAKEUP", 19, internal
# "canIOCTL_SET_BUFFER_WRAPAROUND_MODE", 26, internal
# "canIOCTL_SET_USB_THROTTLE", 28, internal
# "canIOCTL_GET_USB_THROTTLE", 29, internal

# "canIOCTL_LIN_MODE", 45, ???


class IOControl:
    # There's an unusual amount of work to create a docstring, so you can skip
    # it by setting Python's optimization level (with the -O flag).
    if __debug__:
        # Documenting this class is annoying:
        _func_docs = []
        _prop_docs = []

        for name, attr in ATTRIBUTES.items():
            if isinstance(attr, Function):
                if attr.arg is None:
                    args = ''
                else:
                    args = 'value'
                _func_docs.append(
                    """
        .. function:: {name}({args})

           {desc}""".format(
                        name=name, args=args, desc=attr.doc
                    )
                )
                del args

            else:
                assert isinstance(attr, Property)
                _prop_docs.append(
                    """
            {name}: {desc}""".format(
                        name=name, desc=attr['__doc__']
                    )
                )

        del name, attr
        # But now the documentation can be generated:

        __doc__ = """Helper object for using `canIoCtl`

        Provides a variety of functionality, some of which are represented as
        attributes of this object and some as functions. See the respective
        entries below for more information.

        Attributes:
    {props}

    {funcs}
        """.format(
            props=''.join(sorted(_prop_docs)), funcs='\n'.join(sorted(_func_docs))
        )
        del _func_docs, _prop_docs

    def __init__(self, channel):
        self.__dict__['channel'] = channel

    def __dir__(self):
        # Support autocompletion in IDE by adding our attributes
        attrs = set(super().__dir__()) | set(ATTRIBUTES.keys())
        return attrs

    def __getattr__(self, name):
        try:
            attr = ATTRIBUTES[name]
        except KeyError:
            raise AttributeError(
                "{cls} object has no attribute {name}".format(
                    cls=self.__class__.__name__, name=name
                )
            )

        if isinstance(attr, Property):
            if 'getitem' in attr:
                return self._getprop(attr)
            elif 'getfunc' in attr:
                return attr['getfunc'](self)
            else:
                raise AttributeError(
                    "{name} attribute of {cls} object isn't readable".format(
                        name=name, cls=self.__class__.__name__
                    )
                )
        else:
            assert isinstance(attr, Function)
            return self._getfunc(attr)

    def __setattr__(self, name, val):
        try:
            attr = ATTRIBUTES[name]
        except KeyError:
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {name}"
            )

        if isinstance(attr, Property) or 'setitem' in attr:
            self._setprop(attr, val)
        else:
            raise AttributeError(
                "{name} attribute of {cls} object isn't writable".format(
                    name=name, cls=self.__class__.__name__
                )
            )

    def _getfunc(self, func):
        item, arg, ret, doc = func
        assert ret is None, "Return values are not supported"

        if arg is None:
            return lambda: self.raw(item=item)
        else:
            ptype, values, ctype = arg

            def _dynamic_iocontrol_function(val):
                if not isinstance(val, ptype):
                    raise TypeError(
                        "{rec} received, expected {exp}".format(
                            rec=type(val).__name__, exp=ptype.__name__
                        )
                    )
                if val not in values:
                    raise ValueError(
                        f"{val!r} received, expected a value in {values!r}"
                    )

                self.raw(item=item, value=val, ctype=ctype)

            return _dynamic_iocontrol_function

    def _getprop(self, prop):
        item = prop['getitem']
        ctype = prop['ctype']
        ptype = prop['ptype']

        ret = self.raw(item=item, ctype=ctype)
        if ptype:
            if ptype is str:
                ret = ret.decode("utf-8")
            else:
                ret = ptype(ret)
        return ret

    def _setprop(self, prop, val):
        item = prop['setitem']
        ctype = prop['ctype']
        ptype = prop.get('ptype', None)
        values = prop.get('values', None)

        if ptype and not isinstance(val, ptype):
            raise TypeError(
                f"{type(val).__name__} received, expected {ptype.__name__}"
            )
        if values and val not in values:
            raise ValueError(
                f"{val!r} received, expected a value in {values!r}"
            )

        self.raw(item=item, value=val, ctype=ctype)

    def raw(self, item, value=None, ctype=ct.c_uint32):
        """A raw call to `canIoCtl`

        Args:
            item (`IOControlItem`): The "function code" to be passed to `canIoCtl`.

            value: The value sent to `canIoCtl` or `None` if no value should be
                given. Must be compatible with the `ctype` argument.

            ctype: The `ctypes` type that should be used to when sending the
                `value` argument and when interpreting the result of `canIoCtl`.

        """
        buf = ctype()
        if value is not None:
            buf.value = value  # array types must be given their value like this
        dll.canIoCtl(
            self.channel.handle,
            item,
            ct.byref(buf),
            ct.sizeof(buf),
        )
        return buf.value
