import ctypes as ct
import struct
import weakref
from collections import namedtuple
from time import sleep

from .. import deprecation
from ..device import Device
from ..frame import Frame
from . import constants as const
from . import iopin, wrapper
from . import objbuf
from .busparams import BusParamsTq
from .channeldata import HandleData
from .enums import (ChannelFlags, DeviceMode, Driver, MessageFlag,
                    ScriptRequest, ScriptStatus, ScriptStop, Stat)
from .envvar import EnvVar
from .exceptions import CanError
from .iocontrol import IOControl
from .structures import CanBusParamsTq, CanBusStatistics

dll = wrapper.dll


ErrorCounters = namedtuple('ErrorCounters', 'tx rx overrun')
"""Error counters returned by `.Channel.read_error_counters`."""


# canBITRATE_XXX and canFD_BITRATE_XXX constants are still supported.
# However, they are deprecated and as such not mentioned in the docstring.
def openChannel(channel, flags=0, bitrate=None, data_bitrate=None):
    """Open CAN channel

    Retrieves a `Channel` object for the given CANlib channel number using
    the supplied flags.

    Example usage:

        >>> bitrate = canlib.busparams.BusParamsTq(
        ... tq=40,
        ... phase1=5,
        ... phase2=6,
        ... sjw=4,
        ... prescaler=2,
        ... prop=28,
        ... )
        >>> data_bitrate = canlib.busparams.BusParamsTq(
        ... tq=40,
        ... phase1=31,
        ... phase2=8,
        ... sjw=2,
        ... prescaler=2,
        ... )
        >>> ch = canlib.openChannel(
        ... channel=0,
        ... flags=canlib.Open.CAN_FD,
        ... bitrate=bitrate,
        ... data_bitrate=data_bitrate,
        ... )

    Note:

        If both `bitrate` and `data_bitrate` is given, both must be of the same
        type, i.e. either BusParamsTq or BITRATE flags. It is not supported to
        mix the two.

    Args:
        channel (`int`): CANlib channel number
        flags (`int`): Flags, a combination of the `~canlib.canlib.Open` flag values.
            Default is zero, i.e. no flags.

        bitrate (`~busparams.BusParamsTq` or `~canlib.canlib.Bitrate` or `~canlib.canlib.BitrateFD`):
            The desired bitrate. If the bitrate is not a
            `~busparams.BusParamsTq`, the predefined `~canlib.canlib.Bitrate`
            values are used for classic CAN and `~canlib.canlib.BitrateFD`
            values are used for CAN FD, e.g. `canlib.Bitrate.BITRATE_1M` and
            `canlib.BitrateFD.BITRATE_1M_80P`. For CAN FD, this parameter gives the
            arbitration bitrate.

        data_bitrate (`~.busparams.BusParamsTq` or `~canlib.canlib.BitrateFD`):
            The desired data bitrate for CAN FD. If not `~busparams.BusParamsTq` is
            given, the predefined `~canlib.canlib.BitrateFD` values are used, e.g.
            `canlib.BitrateFD.BITRATE_500K_80p`. This parameter is only used
            when opening a CAN FD channel.

    Returns:
        A `Channel` object created with channel and flags

    .. versionadded:: 1.6
        The *bitrate* and *data_bitrate* arguments was added.

    .. versionchanged:: 1.16
        The *bitrate* and *data_bitrate* arguments now accept `~busparams.BusParamsTq` objects.

    .. versionchanged:: 1.17
        Added support for `~canlib.canlib.Bitrate` and `~canlib.canlib.BitrateFD` enumerations.

    """
    ch = Channel(channel, flags)
    is_can_fd = ch.is_can_fd()
    if not is_can_fd and data_bitrate is not None:
        ch.close()
        raise TypeError("data_bitrate was given, but channel was not opened with CAN FD flag.")

    if bitrate is not None:
        if is_can_fd and data_bitrate is None:
            ch.close()
            raise ValueError("data_bitrate must be specified for CAN FD channels.")
        if isinstance(bitrate, BusParamsTq):
            ch.set_bus_params_tq(bitrate, data_bitrate)
        else:
            ch.setBusParams(bitrate)
            if is_can_fd:
                ch.setBusParamsFd(data_bitrate)

    return ch


class ScriptText(str):
    """Text returned by `Channel.scriptGetText`

    Subclass of built-in `str`, so it can be used just like a normal string.

    It also has the following attributes:

    Args:
        text (`str`): Text content.
        slot (`int`): Which script-slot the text came from.
        time (`int`): Timestamp of when the text was printed.
        flags (`~canlib.canlib.Stat`): Any status flags associated with the text.

    .. versionadded:: 1.7

    """

    def __new__(cls, text, slot, time, flags):
        obj = super().__new__(cls, text)
        obj.slot = slot
        obj.time = time
        obj.flags = flags

        return obj


class Channel:
    """Helper class that represents a CANlib channel.

    This class wraps the canlib class and tries to implement a more Pythonic
    interface to CANlib.

    Channels are automatically closed on garbage collection, and can
    also be used as context managers in which case they close as soon as the
    context exits.

    Attributes:
        envvar (`.EnvVar`): Used to access *t* program environment variables

    """

    _iocontrol_ref = lambda self: None  # noqa
    _handledata_ref = lambda self: None  # noqa
    _MAX_MSG_SIZE = 64
    _bus_params_tq_err_msg = (
        "set_bus_params_tq() and get_bus_params_tq() are not "
        "supported on your device. Use setBusParams() and getBusParams() "
        "instead, or try upgrading your firmware.\n\n"
        "Product: {}\n"
        "Firmware version: {}.{}.{}"
    )

    @classmethod
    def _from_handle(cls, handle, allow_close=True):
        def _close(self):
            self.handle = -1

        obj = cls.__new__(cls)
        super().__init__(obj)
        obj.index = None
        obj.handle = handle
        obj.envvar = EnvVar(obj)
        obj._device = None
        # Replace close function with dummy function if not allowed to close
        if not allow_close:
            obj.close = _close.__get__(obj, cls)
        return obj

    def __init__(self, channel_number, flags=0):
        self.index = channel_number
        # Initialize handle here in case canOpenChannel triggers an exception.
        self.handle = -1
        self.handle = dll.canOpenChannel(channel_number, flags)
        self.envvar = EnvVar(self)
        self._device = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        try:
            self.close()
        except CanError:
            # For some reason, in python 2 we get "Handle is invalid (-10)
            # here. Probably something to do with the unpredictable way
            # __del__ is called.
            pass

    def _calculate_length(self, dlc, message_flags):
        if message_flags & MessageFlag.FDF:
            length = dlc
        else:
            length = min(8, dlc)
        return length

    def announceIdentityEx(self, item, value):
        """AnnounceIdentityEx function is used by certain OEM applications.

        .. versionadded:: 1.17

        """
        c_value = ct.c_int(value)
        dll.kvAnnounceIdentityEx(self.handle, item, ct.byref(c_value), ct.sizeof(c_value))

    @property
    def iocontrol(self):
        """`IOControl`: ``canIoCtl`` helper object for this channel

        See the documentation for `IOControl` for how it can be used to perform
        all functionality of the C function ``canIoCtl``.

        Example usage:

            >>> from canlib import canlib
            >>> ch = canlib.openChannel(channel=0)
            >>> ch.iocontrol.timer_scale
            1000
            >>> ch.iocontrol.local_txecho = False

        """
        # Because handles are only closed on garbage collection, a weak
        # reference is used to prevent a cyclic reference that would delay
        # garbage collection (in CPython). As a side effect, the iocontrol
        # objects are optimized to only stay alive while someone needs them.
        ioc = self._iocontrol_ref()
        if ioc is None:
            ioc = IOControl(self)
            self._iocontrol_ref = weakref.ref(ioc)

        return ioc

    @property
    def channel_data(self):
        """`~.channeldata.HandleData`: ``canGetHandleData`` helper object for this channel

        See the documentation for `ChannelData`/`~.channeldata.HandleData` for how it can be
        used to perform all functionality of the C function
        ``canGetHandleData``.

        .. versionadded:: 1.13

        """
        # Because handles are only closed on garbage collection, a weak
        # reference is used to prevent a cyclic reference that would delay
        # garbage collection (in CPython). As a side effect, the handledata
        # objects are optimized to only stay alive while someone needs them.
        chd = self._handledata_ref()
        if chd is None:
            chd = HandleData(self)
            self._handledata_ref = weakref.ref(chd)
        return chd

    def allocate_periodic_objbuf(self, period_us, frame):
        """Allocate a periodic object buffer (a.k.a. auto transmit buffer).

        Call `.objbuf.Periodic.enable()` in order to start the periodic
        transmissions of the CAN frame.

        Args:
            period_us (`int`): Interval in microseconds between each sent CAN frame.
            frame (`~canlib.Frame`): The CAN frame to send.


        Returns:
            `.objbuf.Periodic`: A periodic object buffer.

        .. versionadded:: 1.22

        """
        return objbuf.Periodic(self, period_us, frame)

    def allocate_response_objbuf(self, filter, frame, rtr_only=False):
        """Allocate autoresponse object buffer.

        Args:
            frame (`~canlib.Frame`): The CAN frame to send.
            filter (`.objbuf.MessageFilter`): Messages not matching the filter is ignored.
            rtr_only (`bool`): If `True`, only trigger response on remote requests.


        Returns:
            `.objbuf.Response`: A response object buffer.

        .. versionadded:: 1.22

        """
        return objbuf.Response(self, filter, frame, rtr_only)

    def close(self):
        """Close CANlib channel

        Closes the channel associated with the handle. If no other threads are
        using the CAN circuit, it is taken off bus.

        Note:

            It is normally not necessary to call this function directly, as the
            internal handle is automatically closed when the `Channel` object
            is garbage collected.

        """
        if self.handle != -1:
            dll.canClose(self.handle)
            self.handle = -1

    def canAccept(self, envelope, flag):
        """Set acceptance filters mask or code.

        This routine sets the message acceptance filters on a CAN channel.

        Setting flag to `AcceptFilterFlag.NULL_MASK` (0) removes the filter.

        Note that not all CAN boards support different masks for standard and
        extended CAN identifiers.

        Args:
            envelope:  The mask or code to set.

            flag:      Any of `AcceptFilterFlag`
        """
        dll.canAccept(self.handle, envelope, flag)

    def canSetAcceptanceFilter(self, code, mask, is_extended=False):
        """Set message acceptance filter.

        This routine sets the message acceptance filters on a CAN channel.
        The message is accepted `if id AND mask == code` (this is actually
        imlepemented as `if ((code XOR id) AND mask) == 0`).

        Using standard 11-bit CAN identifiers and setting

        * mask = 0x7f0,
        * code = 0x080

        accepts CAN messages with standard id 0x080 to 0x08f.

        Setting the *mask* to canFILTER_NULL_MASK (0) removes the filter.

        Note that not all CAN boards support different masks for standard and
        extended CAN identifiers.

        Args:
            mask (`int`): A bit mask that indicates relevant bits with '1'.
            code (`int`): The expected state of the masked bits.
            is_extended (`bool`): If `True`, both mask and code applies
                to 29-bit CAN identifiers.
        """
        dll.canSetAcceptanceFilter(self.handle, code, mask, is_extended)

    def device(self):
        """Get a Device object from the current channel

        Returns:
            `~canlib.Device`: Device used by this channel,

        .. versionadded:: 1.16

        """
        if self._device is None:
            chd = self.channel_data
            ean = chd.card_upc_no
            serial = chd.card_serial_no
            self._device = Device(ean=ean, serial=serial)
        return self._device

    def free_objbuf(self):
        """Free all allocated object buffers.

        Free all object buffers allocated via `.allocate_periodic_objbuf()` or
        `.allocate_response_objbuf()`.

        .. versionadded:: 1.22

        """
        dll.canObjBufFreeAll(self.handle)

    def setBusParams(self, freq, tseg1=0, tseg2=0, sjw=0, noSamp=0, syncmode=0):
        """Set bus timing parameters for classic CAN

        This function sets the bus timing parameters for the specified CAN
        controller.

        The library provides default values for tseg1, tseg2, sjw and noSamp
        when freq is a `~canlib.canlib.Bitrate`, e.g. `.Bitrate.BITRATE_1M`.

        If freq is any other value, no default values are supplied by the
        library.

        If you are using multiple handles to the same physical channel, for
        example if you are implementing a multithreaded application, you must
        call `~.Channel.busOn()` once for each handle. The same applies to
        `~.Channel.busOff()` - the physical channel will not go off bus until
        the last handle to the channel goes off bus.

        Args:
            freq: Bitrate in bit/s.
            tseg1: Number of quanta from (but not including) the Sync Segment
                to the sampling point.
            tseg2: Number of quanta from the sampling point to the end of
                the bit.
            sjw: The Synchronization Jump Width, can be 1, 2, 3, or 4.
            nosamp: The number of sampling points, only 1 is supported.
            syncMode: Unsupported and ignored.

        .. versionchanged:: 1.17
            Now accepts `~canlib.canlib.Bitrate` enumerations.

        """
        dll.canSetBusParams(self.handle, freq, tseg1, tseg2, sjw, noSamp, syncmode)

    def getBusParams(self):
        """Get bus timing parameters for classic CAN.

        This function retrieves the current bus parameters for the specified
        channel.

        Returns: A tuple containing:
            *freq*: Bitrate in bit/s.

            *tseg1*: Number of quanta from but not including the Sync
            Segment to the sampling point.

            *tseg2*: Number of quanta from the sampling point to the
            end of the bit.

            *sjw*: The Synchronization Jump Width, can be 1, 2, 3, or 4.

            *noSamp*: The number of sampling points, only 1 is supported.

            *syncmode*: Unsupported, always read as zero.

        """
        freq = ct.c_long()
        tseg1 = ct.c_uint()
        tseg2 = ct.c_uint()
        sjw = ct.c_uint()
        noSamp = ct.c_uint()
        syncmode = ct.c_uint()

        dll.canGetBusParams(
            self.handle,
            ct.byref(freq),
            ct.byref(tseg1),
            ct.byref(tseg2),
            ct.byref(sjw),
            ct.byref(noSamp),
            ct.byref(syncmode),
        )

        return (
            freq.value,
            tseg1.value,
            tseg2.value,
            sjw.value,
            noSamp.value,
            syncmode.value,
        )

    def setBusParamsFd(self, freq_brs, tseg1_brs=0, tseg2_brs=0, sjw_brs=0):
        """Set bus timing parameters for BRS in CAN FD

        This function sets the bus timing parameters used in BRS (Bit rate
        switch) mode for the current CANlib channel.

        The library provides default values for tseg1_brs, tseg2_brs and
        sjw_brs when freq is a `~canlib.canlib.BitrateFD` value, e.g.
        `.BitrateFD.BITRATE_1M_80P`.

        If freq is any other value, no default values are supplied by the
        library.

        For finding out if a channel was opened as CAN FD, use
        `~Channel.is_can_fd()`

        Args:
            freq_brs: Bitrate in bit/s.
            tseg1_brs: Number of quanta from (but not including) the Sync
               Segment to the sampling point.
            tseg2_brs: Number of quanta from the sampling point to the
               end of the bit.
            sjw_brs: The Synchronization Jump Width.

        .. versionchanged:: 1.17
            Now accepts `~canlib.canlib.BitrateFD` enumerations.

        """
        if not self.is_can_fd():
            raise TypeError(
                "setBusParamsFd() is only supported on channels "
                "opened with the CAN_FD or CAN_FD_NONISO flags."
            )
        dll.canSetBusParamsFd(self.handle, freq_brs, tseg1_brs, tseg2_brs, sjw_brs)

    def getBusParamsFd(self):
        """Get bus timing parameters for BRS in CAN FD.

        This function retrieves the bus current timing parameters used in BRS
        (Bit rate switch) mode for the current CANlib channel.

        The library provides default values for tseg1_brs, tseg2_brs and
        sjw_brs when freq is a `~canlib.canlib.BitrateFD` value.

        If freq is any other value, no default values are supplied by the
        library.

        For finding out if a channel was opened as CAN FD, use
        `~Channel.is_can_fd()`

        Returns: A tuple containing:
            *freq_brs*: Bitrate in bit/s.

            *tseg1_brs*: Number of quanta from (but not including) the Sync
            Segment to the sampling point.

            *tseg2_brs*: Number of quanta from the sampling point to the
            end of the bit.

            *sjw_brs*: The Synchronization Jump Width.

        """
        if not self.is_can_fd():
            raise TypeError(
                "getBusParamsFd() is only supported on channels "
                "opened with the CAN_FD or CAN_FD_NONISO flags."
            )
        freq_brs = ct.c_long()
        tseg1_brs = ct.c_uint()
        tseg2_brs = ct.c_uint()
        sjw_brs = ct.c_uint()

        dll.canGetBusParamsFd(
            self.handle,
            ct.byref(freq_brs),
            ct.byref(tseg1_brs),
            ct.byref(tseg2_brs),
            ct.byref(sjw_brs),
        )

        return (freq_brs.value, tseg1_brs.value, tseg2_brs.value, sjw_brs.value)

    def set_bus_params_tq(self, nominal, data=None):
        """Set bus timing parameters, using time quanta

        This function sets the bus timing parameters for the specified CAN
        controller. When setting bus parameters for CAN FD, both `nominal` and
        `data` must be given.

        If you are using multiple handles to the same physical channel, for
        example if you are implementing a multithreaded application, you must
        call `busOff()` once for each handle. The physical channel will not go
        off bus until the last handle to the channel goes off bus.
        The same applies to `busOn()`.

        Args:
            nominal (`~canlib.canlib.busparams.BusParamsTq`): Nominal Bus
                timing parameters, also used for classic CAN

            data (`~canlib.canlib.busparams.BusParamsTq`): Bus timing parameters
                for data rate in CAN FD.

        .. versionadded:: 1.16

        """
        if self.is_can_fd():
            if data is None:
                raise ValueError("data must be specified for CAN FD channels.")
            else:
                dll.canSetBusParamsFdTq(
                    self.handle,
                    CanBusParamsTq._frombusparamstq(nominal),
                    CanBusParamsTq._frombusparamstq(data),
                )
        else:
            dll.canSetBusParamsTq(
                self.handle, CanBusParamsTq._frombusparamstq(nominal)
            )

    def get_bus_params_tq(self):
        """Get bus timing parameters, in time quanta

        This function retrieves the current bus parameters for the specified
        channel. Only the returned `nominal` parameter is valid when classic CAN
        is in use.

        Returns: A `tuple` containing:

            *nominal*: (`~canlib.canlib.busparams.BusParamsTq`) Nominal bus
            timing parameters, also used in classic CAN.

            *data*: (`~canlib.canlib.busparams.BusParamsTq`) Bus timing
            parameters for data rate in CAN FD.

        .. versionadded:: 1.16

        """
        nominal = CanBusParamsTq()
        if self.is_can_fd():
            data = CanBusParamsTq()
            dll.canGetBusParamsFdTq(self.handle, ct.byref(nominal), ct.byref(data))
            return (
                nominal._tobusparamstq(),
                data._tobusparamstq(),
            )
        else:
            dll.canGetBusParamsTq(self.handle, ct.byref(nominal))
            return (
                nominal._tobusparamstq(),
                None,
            )

    def bitrate_to_BusParamsTq(self, freq_a, freq_d=None):
        """Calculate bus parameters based on predefined frequencies.

        This function uses the `~canlib.canlib.Bitrate` and
        `~canlib.canlib.BitrateFD` values to create bus parameters for use with
        the new bus parameter API.

        Args:
            freq_a (`~canlib.canlib.Bitrate` or `~canlib.canlib.BitrateFD`): The bitrate for classic CAN channels specified as a `~canlib.canlib.Bitrate`, or the arbitration bitrate for CAN FD channels specified as a `~canlib.canlib.BitrateFD`.
            freq_d (`~canlib.canlib.BitrateFD`): Data bitrate for CAN FD channels.

        Returns:
            (`nominal`, `None`) for classic CAN, where `nominal` is a `~busparams.BusParamsTq` object.

            (`nominal`, `data`) for CAN FD, where both `nominal` and `data` are `~busparams.BusParamsTq` objects, representing the arbitration bitrate and the data bitrate, respectively.

        .. versionadded:: 1.17

        """
        is_can_fd = self.is_can_fd()
        if is_can_fd and freq_d is None:
            raise ValueError("Data bitrate must be specified for CAN FD channels.")

        nominal = CanBusParamsTq()
        if is_can_fd:
            data = CanBusParamsTq()
            dll.kvBitrateToBusParamsFdTq(
                self.handle,
                freq_a,
                freq_d,
                ct.byref(nominal),
                ct.byref(data))
            return (nominal._tobusparamstq(), data._tobusparamstq())
        else:
            dll.kvBitrateToBusParamsTq(
                self.handle,
                freq_a,
                ct.byref(nominal))
            return (nominal._tobusparamstq(), None)

    def busOn(self):
        """Takes the specified channel on-bus.

        If you are using multiple handles to the same physical channel, for
        example if you are implementing a multithreaded application, you must
        call busOn() once for each handle.

        """
        dll.canBusOn(self.handle)

    def busOff(self):
        """Takes the specified channel off-bus.

        Closes the channel associated with the handle. If no other threads are
        using the CAN circuit, it is taken off bus. The handle can not be used
        for further references to the channel.

        """
        dll.canBusOff(self.handle)

    def _request_bus_statistics(self):
        dll.canRequestBusStatistics(self.handle)

    def _get_bus_statistics(self):
        statistics = CanBusStatistics()
        dll.canGetBusStatistics(self.handle, ct.byref(statistics), ct.sizeof(statistics))
        return statistics

    def get_bus_statistics(self):
        """Return bus statistics.

        Returns:
            `structures.CanBusStatistics`
        """
        statistics = CanBusStatistics()
        dll.canRequestBusStatistics(self.handle)
        sleep(0.01)  # we need to wait for the statistics to be available in windows.
        dll.canGetBusStatistics(self.handle, ct.byref(statistics), ct.sizeof(statistics))
        return statistics

    def getBusOutputControl(self):
        """Get driver type

        This function retrieves the current CAN controller driver type. This
        corresponds loosely to the bus output control register in the CAN
        controller, hence the name of this function.

        Note:

            Not all CAN driver types are supported on all cards.

        Returns:
            drivertype (`.canlib.Driver`): Driver type to set.

        .. versionadded:: 1.11

        """
        driver_type = ct.c_uint()
        dll.canGetBusOutputControl(self.handle, driver_type)
        return Driver(driver_type.value)

    # qqdaca v1.5 This function is complicated by the fact that previously it
    # had the signature of write_wait, and we still want to support that for
    # one more version at least.
    #
    # It would be preferable to merge `write` and `writeWait` by giving `write`
    # an optional `wait` argument. If specified, it would make the function
    # call `canWriteWait` with ``timeout=wait``. However, that would complicate
    # the function too much if the old signature is still to be supported.
    #
    # If this merger is done in the future, also add the same argument to
    # linlib's `writeMessage` and `requestMessage` functions.
    def write(self, frame=None, *args, **kwargs):
        """Send a CAN message.

        This function sends a Frame object as a CAN message. Note that the
        message has been queued for transmission when this calls return. It has
        not necessarily been sent.

        Note:

            If you are using the same channel via multiple handles, the default
            behaviour is that the different handles will "hear" each other just
            as if each handle referred to a channel of its own. If you open,
            say, channel 0 from thread A and thread B and then send a message
            from thread A, it will be "received" by thread B.

            This behaviour can be changed by setting `local_txecho` to `False`
            (using `~canlib.canlib.IOControl`):

            >>> from canlib import canlib
            >>> ch = canlib.openChannel(channel=0)
            >>> ch.iocontrol.local_txecho = False

        Also see `Channel.write_raw` for sending messages without constructing
        `canlib.Frame` objects.

        .. deprecated:: 1.5
           Sending the `canlib.Frame` contents as separate arguments; this
           functionality has been taken over by `write_raw`.

        Args:
            frame (`canlib.Frame`)

        """
        if len(args) == 0 and len(kwargs) == 0:
            dll.canWrite(self.handle, frame.id, bytes(frame.data), frame.dlc, frame.flags)
        else:
            deprecation.manual_warn(
                "Calling Channel.write() with individual arguments is deprecated, "
                "please use a Frame object or Channel.write_raw()"
            )
            if frame is None:
                return self.write_raw(*args, **kwargs)
            else:
                return self.write_raw(frame, *args, **kwargs)

    def write_raw(self, id_, msg, flag=0, dlc=None):
        """Send a CAN message

        See docstring of `Channel.write` for general information about sending
        CAN messages.

        The variable name id (as used by canlib) is a built-in function in
        Python, so the name `id_` is used instead.

        Args:
            id_: The identifier of the CAN message to send.
            msg: An array or bytearray of the message data
            flag: A combination of `~canlib.canlib.MessageFlag`. Use this
                parameter e.g. to send extended (29-bit) frames.
            dlc: The length of the message in bytes. For Classic CAN dlc can
                be at most 8, unless `.Open.ACCEPT_LARGE_DLC` is
                used. For CAN FD dlc can be one of the following 0-8, 12, 16,
                20, 24, 32, 48, 64. Optional, if omitted, *dlc* is calculated
                from the *msg* array.

        """  # noqa: RST306
        if not isinstance(msg, (bytes, str)):
            if not isinstance(msg, bytearray):
                msg = bytearray(msg)
            msg = bytes(msg)
        if dlc is None:
            dlc = len(msg)
        dll.canWrite(self.handle, id_, msg, dlc, flag)

    def writeSync(self, timeout):
        """Wait for queued messages to be sent

        Waits until all CAN messages for the specified handle are sent, or the
        timeout period expires.

        Args:
            timeout (`int`): The timeout in milliseconds, `None` or ``0xFFFFFFFF`` for
                an infinite timeout.

        """
        if timeout is None:
            timeout = 0xFFFFFFFF
        dll.canWriteSync(self.handle, timeout)

    def writeWait(self, frame, timeout, *args, **kwargs):
        """Sends a CAN message and waits for it to be sent.

        This function sends a CAN message. It returns when the message is sent,
        or the timeout expires. This is a convenience function that combines
        write() and writeSync().

        .. deprecated:: 1.5
           Sending the `Frame` contents as separate arguments; this
           functionality has been taken over by `writeWait_raw`.

        Args:
            frame (`canlib.Frame`) : Frame containing the CAN data to be sent
            timeout (`int`) : The timeout, in milliseconds. 0xFFFFFFFF gives an infinite
                timeout.
        """
        if len(args) == 0 and len(kwargs) == 0:
            dll.canWriteWait(
                self.handle, frame.id, bytes(frame.data), frame.dlc, frame.flags, timeout
            )
        else:
            deprecation.manual_warn(
                "Calling Channel.writeWait() with individual arguments is deprecated, "
                "please use a Frame object or Channel.writeWait_raw()"
            )
            return self.writeWait_raw(frame, timeout, *args, **kwargs)

    def writeWait_raw(self, id_, msg, flag=0, dlc=0, timeout=0):
        """Sends a CAN message and waits for it to be sent.

        This function sends a CAN message. It returns when the message is sent,
        or the timeout expires. This is a convenience function that combines
        write() and writeSync().

        Args:
            id_: The identifier of the CAN message to send.
            msg: An array or bytearray of the message data
            flag: A combination of `canlib.canlib.MessageFlag`. Use this
                parameter e.g. to send extended (29-bit) frames.
            dlc: The length of the message in bytes. For Classic CAN dlc can
                be at most 8, unless `canlib.canlib.Open.ACCEPT_LARGE_DLC` is
                used. For CAN FD dlc can be one of the following 0-8, 12, 16,
                20, 24, 32, 48, 64. Optional, if omitted, dlc is calculated
                from the msg array.
            timeout: The timeout, in milliseconds. 0xFFFFFFFF gives an infinite
                timeout.

        """  # noqa: RST306
        if not isinstance(msg, (bytes, str)):
            if not isinstance(msg, bytearray):
                msg = bytearray(msg)
            msg = bytes(msg)

        if dlc == 0:
            dlc = len(msg)

        dll.canWriteWait(self.handle, id_, msg, dlc, flag, timeout)

    def readTimer(self):
        """Read the hardware clock on the specified device

        Returns the time value.
        """
        time = ct.c_int()
        dll.kvReadTimer(self.handle, time)
        return time.value

    def read(self, timeout=0):
        """Read a CAN message and metadata.

        Reads a message from the receive buffer. If no message is available,
        the function waits until a message arrives or a timeout occurs.

        The unit of the returned `.Frame.timestamp` is configurable using
        `Channel.iocontrol.timer_scale`, default is 1 ms.

        Note:

            If you are using the same channel via multiple handles, the default
            behaviour is that the different handles will "hear" each other just
            as if each handle referred to a channel of its own. If you open,
            say, channel 0 from thread A and thread B and then send a message
            from thread A, it will be "received" by thread B.

            This behaviour can be changed by setting `local_txecho` to `False`
            (using `~canlib.canlib.IOControl`):

            >>> from canlib import canlib
            >>> ch = canlib.openChannel(channel=0)
            >>> ch.iocontrol.local_txecho = False

        Args:
            timeout (`int`):  Timeout in milliseconds, -1 gives an
                infinite timeout.

        Returns:
            `canlib.Frame`

        Raises:
            `~canlib.canlib.CanNoMsg`: No CAN message is currently available.

        """
        # msg will be replaced by class when CAN FD is supported
        msg = ct.create_string_buffer(self._MAX_MSG_SIZE)
        id_ = ct.c_long()
        dlc = ct.c_uint()
        flag = ct.c_uint()
        time = ct.c_ulong()
        dll.canReadWait(self.handle, id_, msg, dlc, flag, time, timeout)
        try:
            flags = MessageFlag(flag.value)
            # In Python 2 this will fail because the value is a C long, and the
            # enums only accept int.
        except ValueError:
            flags = MessageFlag(int(flag.value))

        length = self._calculate_length(dlc.value, flags)
        return Frame(
            id_=id_.value,
            data=bytearray(msg.raw[:length]),
            dlc=dlc.value,
            flags=flags,
            timestamp=time.value,
        )

    def readDeviceCustomerData(self, userNumber=100, itemNumber=0):
        """Read customer data stored in device"""
        buf = ct.create_string_buffer(8)
        user = ct.c_int(userNumber)
        item = ct.c_int(itemNumber)
        dll.kvReadDeviceCustomerData(self.handle, user, item, buf, ct.sizeof(buf))
        return struct.unpack('!Q', buf)[0]

    def readSpecificSkip(self, id_):
        """Read a message with specified identifier

        Reads a message with a specified identifier from the receive
        buffer. Any preceding message not matching the specified identifier
        will be removed in the receive buffer. If no message with the specified
        identifier is available, the function returns immediately with an error
        code.

        The unit of the returned `.Frame.timestamp` is configurable using
        `Channel.iocontrol.timer_scale`, default is 1 ms.

        Returns:
            `canlib.Frame`

        """
        # msg will be replaced by class when CAN FD is supported
        msg = ct.create_string_buffer(self._MAX_MSG_SIZE)
        id_ = ct.c_long(id_)
        dlc = ct.c_uint()
        flag = ct.c_uint()
        time = ct.c_ulong()
        dll.canReadSpecificSkip(self.handle, id_, msg, dlc, flag, time)
        try:
            flags = MessageFlag(flag.value)
            # In Python 2 this will fail because the value is a long, and the
            # enums only accept int.
        except ValueError:
            flags = MessageFlag(int(flag.value))

        length = self._calculate_length(dlc.value, flags)
        return Frame(
            id_=id_.value,
            data=bytearray(msg.raw[:length]),
            dlc=dlc.value,
            flags=flags,
            timestamp=time.value,
        )

    def requestChipStatus(self):
        """Request chip status messages

        Requests that the hardware report the chip status (bus on/error passive
        status etc.) to the driver. The chip status can later be retrieved
        using `canlib.Channel.readStatus`.

        Note:

            The `requestChipStatus` function is asynchronous, that is, it
            completes before the answer is returned from the hardware.  The
            time between a call to `requestChipStatus` and the point in time
            where the chip status is actually available via a call to
            `.Channel.readStatus` is not defined. The
            `.Channel.readStatus` always returns the latest data reported
            by the hardware.

        """
        dll.canRequestChipStatus(self.handle)

    def readStatus(self):
        """Return status for the current channel

        Returns the latest status reported by the hardware in a combination of
        the flags `~canlib.canlib.Stat` (bus on/error passive + status etc).

        Returns:
            `canlib.canlib.Stat`

        """
        flags = ct.c_ulong(0)
        dll.canReadStatus(self.handle, ct.byref(flags))
        return Stat(flags.value)

    def readSyncSpecific(self, id_, timeout=0):
        """Wait until the receive queue contains a message with the specified id"""
        id_ = ct.c_long(id_)
        dll.canReadSyncSpecific(self.handle, id_, timeout)

    def read_error_counters(self):
        """Read the error counters of the CAN controller

        Returns the latest known values of the error counters in the specified
        circuit. If the error counters change values precisely when
        `read_error_counters` is called, it may not be reflected in the
        returned result.

        Use `.clear_error_counters` via `.Channel.iocontrol` to clear
        the counters.

        Returns:
            The returned tuple is a ``(rx, tx, overrun)`` named tuple of:

            #. ``rx`` (`int`): Receive error counter
            #. ``tx`` (`int`): Transmit error counter
            #. ``overrun`` (`int`): Number of overrun errors.

        .. versionadded:: 1.11

        """
        txErr = ct.c_int()
        rxErr = ct.c_int()
        ovErr = ct.c_int()
        dll.canReadErrorCounters(self.handle, ct.byref(txErr), ct.byref(rxErr), ct.byref(ovErr))
        error_counters = ErrorCounters(
            tx=txErr.value,
            rx=rxErr.value,
            overrun=ovErr.value,
        )
        return error_counters

    def scriptSendEvent(
        self, slotNo=0, eventType=const.kvEVENT_TYPE_KEY, eventNo=None, data=0
    ):
        """Send specified event to specified t script

        Send an event with given type, event number, and associated data to a
        script running in a specific slot.

        """
        if eventNo is None:
            ord('a')
        dll.kvScriptSendEvent(
            self.handle, ct.c_int(slotNo), ct.c_int(eventType), ct.c_int(eventNo), ct.c_uint(data)
        )

    def setBusOutputControl(self, drivertype=Driver.NORMAL):
        """Set driver type

        This function sets the driver type for a CAN controller to e.g. silent
        mode. This corresponds loosely to the bus output control register in
        the CAN controller, hence the name of this function.

        Note:

            Not all CAN driver types are supported on all cards.

        Args:
            drivertype (`.canlib.Driver`): Driver type to set.

        """
        dll.canSetBusOutputControl(self.handle, drivertype)

    @deprecation.deprecated.favour(".iocontrol.flush_rx_buffer()")
    def ioCtl_flush_rx_buffer(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `IOControl`; ``Channel.iocontrol.flush_rx_buffer()``.

        """
        dll.canIoCtl(self.handle, const.canIOCTL_FLUSH_RX_BUFFER, None, 0)

    @deprecation.deprecated.favour("'Channel.iocontrol.timer_scale = scale'")
    def ioCtl_set_timer_scale(self, scale):
        """Deprecated function

        .. deprecated:: 1.5
           Use `IOControl`; ``Channel.iocontrol.timer_scale = scale``

        """
        scale = ct.c_long(scale)
        dll.canIoCtl(
            self.handle, const.canIOCTL_SET_TIMER_SCALE, ct.byref(scale), ct.sizeof(scale)
        )

    @deprecation.deprecated.favour("'Channel.iocontrol.report_access_errors' attribute")
    def ioCtl_get_report_access_errors(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `IOControl`; ``Channel.iocontrol.report_access_errors``

        """
        buf = ct.c_ubyte()
        dll.canIoCtl(
            self.handle, const.canIOCTL_GET_REPORT_ACCESS_ERRORS, ct.byref(buf), ct.sizeof(buf)
        )
        return buf.value

    @deprecation.deprecated.favour("'Channel.iocontrol.report_access_errors = True'")
    def ioCtl_set_report_access_errors(self, on=0):
        """Deprecated function

        .. deprecated:: 1.5
           Use `IOControl`; ``Channel.iocontrol.report_access_errors = True``

        """
        buf = ct.c_ubyte(on)
        dll.canIoCtl(
            self.handle, const.canIOCTL_SET_REPORT_ACCESS_ERRORS, ct.byref(buf), ct.sizeof(buf)
        )

    def flashLeds(self, action, timeout_ms):
        """Turn Leds on or off.

        Args:
            action (`int`): One of `~canlib.canlib.LEDAction`, defining
                          which LED to turn on or off.
            timeout_ms (`int`): Specifies the time, in milliseconds, during which
                              the action is to be carried out. When the timeout
                              expires, the LED(s) will return to its ordinary
                              function.
        """
        dll.kvFlashLeds(self.handle, action, timeout_ms)

    @deprecation.deprecated.favour("ChannelData.device_name")
    def getChannelData_Name(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData.device_name``

        """
        return wrapper.getChannelData_Name(self.index)

    @deprecation.deprecated.favour("ChannelData.custom_name")
    def getChannelData_Cust_Name(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData.custom_name``

        """
        try:
            return wrapper.getChannelData_Cust_Name(self.index)
        except CanError:
            None
            return ""
        return ""

    @deprecation.deprecated.favour("ChannelData.chan_no_on_card")
    def getChannelData_Chan_No_On_Card(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData.chan_no_on_card``

        """
        return wrapper.getChannelData_Chan_No_On_Card(self.index)

    @deprecation.deprecated.favour("ChannelData.card_number")
    def getChannelData_CardNumber(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData.card_number``

        """
        return wrapper.getChannelData_CardNumber(self.index)

    @deprecation.deprecated.favour("ChannelData.card_upc_no")
    def getChannelData_EAN(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData.card_upc_no``

        """
        return wrapper.getChannelData_EAN(self.index)

    @deprecation.deprecated
    def getChannelData_EAN_short(self):
        return wrapper.getChannelData_EAN_short(self.index)

    @deprecation.deprecated.favour("ChannelData.card_serial_no")
    def getChannelData_Serial(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData.card_serial_no``

        """
        return wrapper.getChannelData_Serial(self.index)

    @deprecation.deprecated.favour("ChannelData.driver_name")
    def getChannelData_DriverName(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData.driver_name``

        """
        return wrapper.getChannelData_DriverName(self.index)

    @deprecation.deprecated.favour("ChannelData.card_firmware_rev")
    def getChannelData_Firmware(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData.card_firmware_rev``

        """
        return wrapper.getChannelData_Firmware(self.index)

    def scriptStart(self, slot):
        """Start previously loaded script in specified slot"""
        dll.kvScriptStart(self.handle, slot)

    def scriptStatus(self, slot):
        """Retreives t program status for selected slot

        Args:
            slot (`int`) : Slot number to be queried

        Returns:
            `canlib.ScriptStatus`

        .. versionadded:: 1.6

        """
        status = ct.c_uint()
        dll.kvScriptStatus(self.handle, slot, ct.byref(status))
        return ScriptStatus(status.value)

    def scriptStop(self, slot, mode=ScriptStop.NORMAL):
        """Stop script running in specified slot


        Args:
            slot (`int`) : slot containing the running script we want to stop.
            mode (`canlib.ScriptStop`) : Default mode is `canlib.ScriptStop.NORMAL`.

        """
        dll.kvScriptStop(self.handle, slot, mode)

    def scriptUnload(self, slot):
        """Unload previously stopped script in specified slot"""
        dll.kvScriptUnload(self.handle, slot)

    def scriptLoadFileOnDevice(self, slot, localFile):
        """Load compiled, locally stored, script file

        Loads a compiled script file (.txe) stored locally on the device (SD
        card) into a script slot on the device. The scripts default channel
        will be the same channel used when this Channel object was created.

        Args:
            slot (`int`) : slot containing the running script we want to stop.
            localFile (`str`): Name of compiled script (.txe) to load.

        """
        dll.kvScriptLoadFileOnDevice(self.handle, slot, ct.c_char_p(localFile))

    def scriptLoadFile(self, slot, filePathOnPC):
        """Load compiled script file from host(PC)

        Loads a compiled script file (.txe) stored on the host (PC) into a
        script slot on the device. The scripts default channel will be the same
        channel used when this Channel object was created.

        Args:
            slot (`int`) : slot containing the running script we want to stop.
            filePathOnPC (`str`): Path to compiled script (.txe) to load.

        """
        c_filePathOnPC = ct.c_char_p(filePathOnPC.encode('utf-8'))
        dll.kvScriptLoadFile(self.handle, slot, c_filePathOnPC)

    def scriptEnvvarOpen(self, name):
        """Low level function to open an Envvar

        This should normally not be used directly, instead opening and closing
        of an envvar is automatically done when accessing via the `EnvVar`
        class through `Channel.envvar`

        """
        envvarType = ct.c_int()
        envvarSize = ct.c_int()
        envvarName = ct.create_string_buffer(name.encode('utf-8'))
        envHandle = dll.kvScriptEnvvarOpen(
            self.handle, envvarName, ct.byref(envvarType), ct.byref(envvarSize)
        )
        return envHandle, envvarType.value, envvarSize.value

    def scriptEnvvarClose(self, envHandle):
        """Low level function to close an Envvar

        This should normally not be used directly, instead opening and closing
        of an envvar is automatically done when accessing via the `EnvVar`
        class through `Channel.envvar`

        """
        dll.kvScriptEnvvarClose(ct.c_int64(envHandle))

    def scriptEnvvarSetInt(self, envHandle, value):
        """Low level function to set an Envvar of type int

        This should normally not be used directly, instead set and get the
        value of an envvar using the `EnvVar` class through `Channel.envvar`

        """
        value = int(value)
        dll.kvScriptEnvvarSetInt(ct.c_int64(envHandle), ct.c_int(value))

    def scriptEnvvarGetInt(self, envHandle):
        """Low level function to read an Envvar of type int

        This should normally not be used directly, instead set and get the
        value of an envvar using the `EnvVar` class through `Channel.envvar`

        """
        envvarValue = ct.c_int()
        dll.kvScriptEnvvarGetInt(ct.c_int64(envHandle), ct.byref(envvarValue))
        return envvarValue.value

    def scriptEnvvarSetFloat(self, envHandle, value):
        """Low level function to set an Envvar of type float

        This should normally not be used directly, instead set and get the
        value of an envvar using the `EnvVar` class through `Channel.envvar`

        """
        value = float(value)
        dll.kvScriptEnvvarSetFloat(ct.c_int64(envHandle), ct.c_float(value))

    def scriptEnvvarGetFloat(self, envHandle):
        """Low level function to read an Envvar of type float

        This should normally not be used directly, instead set and get the
        value of an envvar using the `EnvVar` class through `Channel.envvar`

        """
        envvarValue = ct.c_float()
        dll.kvScriptEnvvarGetFloat(ct.c_int64(envHandle), ct.byref(envvarValue))
        return envvarValue.value

    @deprecation.deprecated.favour(".script_envvar_set_data()")
    def scriptEnvvarSetData(self, envHandle, value, envSize):
        value_p = ct.create_string_buffer(value.encode('utf-8'))
        dll.kvScriptEnvvarSetData(ct.c_int64(envHandle), value_p, 0, ct.c_int(envSize))

    def script_envvar_set_data(self, envHandle, value, len, start=0):
        """Low level function to write a slice of an Envvar of type char

        This should normally not be used directly, instead set and get the
        value of an envvar using the `EnvVar` class through `Channel.envvar`

        `value` needs to be a bytes-like object or list

        .. versionadded:: 1.10

        """
        if isinstance(value, list):
            value = bytes(value)

        char_array = ct.c_char * len
        value_p = char_array.from_buffer_copy(value)
        dll.kvScriptEnvvarSetData(ct.c_int64(envHandle), value_p, start, len)

    @deprecation.deprecated.favour(".script_envvar_get_data()")
    def scriptEnvvarGetData(self, envHandle, envSize):
        envvarValue = ct.create_string_buffer(envSize)
        dll.kvScriptEnvvarGetData(
            ct.c_int64(envHandle), ct.byref(envvarValue), 0, ct.c_int(envSize)
        )
        return envvarValue.value

    def script_envvar_get_data(self, envHandle, len, start=0):
        # rename to length?
        """Low level function to read a slice of an Envvar of type char

        This should normally not be used directly, instead set and get the
        value of an envvar using the `EnvVar` class through `Channel.envvar`

        .. versionadded:: 1.10

        """
        char_array = (ct.c_char * len)()
        dll.kvScriptEnvvarGetData(ct.c_int64(envHandle), ct.byref(char_array), start, len)
        return bytes(char_array)

    def scriptGetText(self):
        """Read text from subscribed script slots

        Text-subscriptions must first be set up with
        `Channel.scriptRequestText`.

        Returns:
            `ScriptText`

        Raises:
            `~canlib.canlib.CanNoMsg`: No more text is currently available.

        .. versionadded:: 1.7

        """
        slot = ct.c_int()
        time = ct.c_ulong()
        flags = ct.c_uint()
        text = ct.create_string_buffer(1024)

        dll.kvScriptGetText(
            self.handle,
            ct.byref(slot),
            ct.byref(time),
            ct.byref(flags),
            text,
            ct.sizeof(text),
        )

        return ScriptText(text.value.decode('utf-8'), slot.value, time.value, Stat(flags.value))

    def scriptRequestText(self, slot, request=ScriptRequest.SUBSCRIBE):
        """Set up a printf subscription to a selected script slot

        Arguments:
            slot (`int`): The script slot to subscribe/unsubscribe from.
            request(`~canlib.canlib.ScriptRequest`): Whether to subscribe or unsubscribe.

        Text printed with ``printf()`` by a t-program that you are subscribed to
        is saved and can be retrieved with `Channel.scriptGetText`.

        .. versionadded:: 1.7

        """
        dll.kvScriptRequestText(self.handle, slot, request)

    def set_callback(self, function, event, context=None):
        """Register callback function

        This will register a callback function which is called when certain
        events occur. You can register at most one callback function per handle
        at any time.

        Note:

        The callback function is called in the context of a high-priority
        thread created by CANlib. You should take precaution not to do any time
        consuming tasks in the callback.

        Small example of usage::

            # Declare callback function
            def callback_func(hnd, context, event):
                event = canlib.Notify(event)

                # The nonlocal statement causes the listed identifiers to refer
                # to previously bound variables in the nearest enclosing scope
                # excluding globals.
                nonlocal callback_has_been_called
                print("Callback called, context:{}, event:{!r}".format(context, event))
                # Notify the main program by setting the flag
                callback_has_been_called = True

            # setup communication variable and callback
            callback_has_been_called = False
            callback = canlib.dll.KVCALLBACK_T(callback_func)

            with canlib.openChannel(0) as ch:
            ch.set_callback(callback, context=121, event=canlib.Notify.BUSONOFF)
            # trigger the callback
            ch.busOn()
            # do something else
            time.sleep(0.5)
            # Verify that the callback was triggered
            assert callback_has_been_called

        Note:

        It is very important to make sure that you keep a reference to the
        callback type (``callback`` in the sample above) for as long as any C
        library might call it. If it gets deleted by the garbage collector,
        calling it from C is likely to either cause a segfault or maybe even
        interpret random memory as machine language.

        Arguments:
            function (`~canlib.canlib.KVCALLBACK_T`): A ctypes wrapped Python function

            event (`~canlib.canlib.Notify`): A combination of flags to indicate
                what events to trigger on

        .. versionadded:: 1.7

        """
        dll.kvSetNotifyCallback(self.handle, function, context, event)

    def fileDiskFormat(self):
        """Format the disk on the device, not supported by all devices.

        .. versionadded:: 1.11
        """
        dll.kvFileDiskFormat(self.handle)

    def fileGetCount(self):
        """Get the number of files on the device.

        Returns:
            `int`: The number of files.
        """
        count = ct.c_int()
        dll.kvFileGetCount(self.handle, ct.byref(count))
        return count.value

    def fileGetName(self, fileNo):
        """Get the name of the file with the supplied number.

        Args:
            fileNo (`int`): The number of the file.

        Returns:
            `str`: The name of the file.
        """
        fileName = ct.create_string_buffer(50)
        dll.kvFileGetName(self.handle, ct.c_int(fileNo), fileName, ct.sizeof(fileName))
        return fileName.value.decode('utf-8')

    def fileDelete(self, deviceFileName):
        """Delete file from device."""
        dll.kvFileDelete(self.handle, deviceFileName.encode('utf-8'))

    def fileCopyToDevice(self, hostFileName, deviceFileName=None):
        """Copy an arbitrary file from the host to the () isdevice.

        The filename must adhere to the FAT '8.3' naming standard, max 8
        characters - a dot - max 3 characters.

        Args:
            hostFileName (`str`):   The target host file name.
            deviceFileName (`str`, optional): The device file name.
                Defaults to the same as *hostFileName*.

        """
        if deviceFileName is None:
            deviceFileName = hostFileName
        dll.kvFileCopyToDevice(
            self.handle, hostFileName.encode('utf-8'), deviceFileName.encode('utf-8')
        )

    def fileCopyFromDevice(self, deviceFileName, hostFileName=None):
        """Copy an arbitrary file from the device to the host.

        Args:
            deviceFileName (`str`): The device file name.
            hostFileName (`str`, optional):   The target host file name.
                Defaults to deviceFileName.
        """
        if hostFileName is None:
            hostFileName = deviceFileName
        dll.kvFileCopyFromDevice(
            self.handle, deviceFileName.encode('utf-8'), hostFileName.encode('utf-8')
        )

    def kvDeviceSetMode(self, mode):
        """Set the current device's mode.

        Note:

            The mode is device specific, which means that not all modes are
            implemented in all products.

        Args:
            mode (`int`): One of `~canlib.canlib.DeviceMode`, defining which
                        mode to use.

        """
        dll.kvDeviceSetMode(self.handle, ct.c_int(mode))

    def kvDeviceGetMode(self):
        """Read the current device's mode.

        Note:

            The mode is device specific, which means that not all modes are
            implemented in all products.

        Returns:
            `int`: One of `DeviceMode`, indicating which mode is in use.

        """
        mode = ct.c_int()
        dll.kvDeviceGetMode(self.handle, ct.byref(mode))
        return DeviceMode(mode.value)

    def number_of_io_pins(self):
        """Return the total number of available I/O pins

        .. versionadded:: 1.8

        """
        pin_count = ct.c_uint()
        dll.kvIoGetNumberOfPins(self.handle, ct.byref(pin_count))
        return pin_count.value

    def io_pins(self):
        """Generator that returns all I/O pins one by one

        Returns object depending on pin type and direction: `iopin.AnalogIn`,
        `iopin.AnalogOut`, `iopin.DigitalIn`, `iopin.DigitalOut` or
        `iopin.Relay`.

        .. versionadded:: 1.8

        """
        for index in range(self.number_of_io_pins()):
            yield iopin.get_io_pin(channel=self, index=index)

    def io_confirm_config(self):
        """Confirm current I/O configuration

        It is required to confirm a configuration by calling this function
        before accessing any I/O pins value.

        .. versionadded:: 1.8

        """
        dll.kvIoConfirmConfig(self.handle)

    def get_io_pin(self, index):
        """Return I/O pin using *index*

        Returns:
            `iopin.IoPin`: io pin object for *index* (Any of `iopin.AnalogIn`,
            `iopin.DigitalOut` etc)

        .. versionadded:: 1.8

        """
        return iopin.get_io_pin(channel=self, index=index)

    def is_can_fd(self):
        """Return `True` if the channel has been opened with the
        `~Open.CAN_FD` or `~Open.CAN_FD_NONISO` flags.

        Returns:
            `True` if CAN FD, `False` otherwise.

        .. versionadded: 1.17

        """
        flags = self.channel_data.channel_flags
        return ChannelFlags.IS_CANFD in flags
