import ctypes as ct
import datetime

from .. import VersionNumber, canlib
from .enums import Device
from .enums import SoftwareInfoItem as swinfo
from .kmf import KmfSystem
from .log import MountedLog, UnmountedLog
from .wrapper import dll


def _openDevice(channel_number, device_type):
    card_no = canlib.ChannelData(channel_number).card_number
    status_p = ct.c_int()
    handle = dll.kvmDeviceOpen(card_no, ct.byref(status_p), device_type)
    return handle


def openDevice(channel_number, mount=False, device_type=Device.MHYDRA_EXT):
    """Open a Memorator device

    Arguments:

        channel_number (`int`): A channel number of the Memorator to be opened.

        mount (`bool`): Whether the memorator log area should be mounted before
            returned.

        device_type (`.Device`): The type of the memorator to be
            opened (defaults to `.Device.MHYDRA_EXT`)

    Returns:
        `Memorator`

    .. versionadded:: 1.6

    """
    handle = _openDevice(channel_number, device_type)
    memo = Memorator(handle, channel_number, device_type)
    if mount:
        try:
            memo.mount()
        except Exception:
            memo.close()
            raise

    return memo


class Memorator(KmfSystem):
    """A Memorator device opened with `openDevice`

    This class should not be instantiated directly, instead call `openDevice`.

    A device opened as `Memorator` can be configured from XML using
    `.kvamemolibxml.load_xml_file` and `.write_config`::

        # Read the original XML file (config.xml)
        config = kvamemolibxml.load_xml_file("config.xml")

        # Validate the XML
        errors, warnings = config.validate()
        if errors or warnings:
            print(errors)
            print(warnings)
            raise Exception("One or more errors/warnings in xml configuration")

        # Write the configuration in binary
        memorator.write_config(config.lif)

    The configuration can then be read back (in binary)::

        dev.read_config()

    The log files on the device can be accessed via the `log` attribute. By
    default, the log area is not mounted so only a few operations are allowed,
    such as getting the number of log files::

        num_log_files = len(memorator.log)

    For a full list of allowed operations, see `.UnmountedLog`
    (the type of ``.log`` before a mount).

    The log area can be mounted either with `openDevice`'s `mount` argument set
    to `True`, or later with the `Memorator.mount` function. Once this is done
    the `log` attribute is a `.MountedLog` which supports getting log files as
    `.LogFile` objects::

        # We can index the Memorator object if we know what file we want
        log_file_number_two = memorator.log[2]

        # Although usually we want to loop through all log files
        for log_file in memorator.log:
            ...

    See the documentation of `.MountedLog` for all available operations.

    Args:

        channel_number (`int`): The channel number that was used to connect to
            this memorator.

        device_type (`~canlib.kvmlib.Device`): The device type that was used to
            connect to this memorator.

        mounted (`bool`): Whether the device's memory card has been mounted.

    .. versionadded:: 1.6

    """

    _ASSUMED_CONFIG_SIZE = 4096

    mounted = None

    def __init__(self, handle, channel_number, device_type):
        super().__init__(handle)
        self.channel_number = channel_number
        self.device_type = device_type

        # Dummy object until we have mounted the actual log
        self.log = UnmountedLog(self)
        self.mounted = False

    @property
    def config_version_needed(self):
        """`canlib.VersionNumber`: The version of param.lif that the connected device expects"""
        return self._get_software_info(swinfo.DRIVER)

    @property
    def disk_size(self):
        """`int`: The disk size in megabytes

        Warning:

            This is not necessarily the amount of space available for
            allocation; ``Memorator.format_disk(reserved_space=Memorator.disk_size)`` is
            not guaranteed to succeed.

            The most reliable way of calculating reserved space is to first
            format the disk with `.reserved_space` set to ``0``, and then use
            `Memorator.disk_usage.total`.

        """
        size = ct.c_uint32()
        dll.kvmDeviceDiskSize(self.handle, ct.byref(size))
        size = int(size.value * 512) / 10 ** 6  # convert to MB
        return size

    @property
    def driver_version(self):
        """`canlib.VersionNumber`: The used driver version information"""
        return self._get_software_info(swinfo.DRIVER)

    @property
    def firmware_version(self):
        """`canlib.VersionNumber`: The device firmware version information"""
        return self._get_software_info(swinfo.FIRMWARE)

    @property
    def kvmlib_version(self):
        """`canlib.VersionNumber`: Returns the version of kvmlib"""
        return self._get_software_info(swinfo.KVMLIB)

    @property
    def rtc(self):
        """`datetime.datetime`: The value of the real-time clock"""
        t = ct.c_uint32()
        dll.kvmDeviceGetRTC(self.handle, ct.byref(t))
        return datetime.datetime.fromtimestamp(t.value)

    @rtc.setter
    def rtc(self, val):
        dll.kvmDeviceSetRTC(self.handle, int(val.timestamp()))

    @property
    def serial_number(self):
        """`int`: The serial number of the Memorator"""
        serial = ct.c_uint()
        dll.kvmDeviceGetSerialNumber(self.handle, ct.byref(serial))
        return serial.value

    def flash_leds(self):
        """Flash all LEDs on the Memorator"""
        dll.kvmDeviceFlashLeds(self.handle)

    def mount(self):
        """Mount the Memorator's log area

        This replaces the object `log` attribute with a `MountedLog`, which
        allows access to log files.

        If the log has already been mounted (``self.mounted == True``), this is
        a no-op.

        """
        if not self.mounted:
            major = ct.c_int()
            minor = ct.c_int()
            dll.kvmDeviceMountKmfEx(self.handle, ct.byref(major), ct.byref(minor))
            ldf_version = VersionNumber(major.value, minor.value)

            # Now that we're mounted, replace the dummy object with the proper
            # log object.
            self.log = MountedLog(self, ldf_version=ldf_version)
            self.mounted = True

            # We need to be allowed to mount log files.
            # Beetlegeuse Beetlegeuse Beetlegeuse.
            len(self.log)

    def format_disk(self, reserved_space=10, database_space=2, fat32=True):
        """Format the SD memory card in the Memorator

        Arguments:
            reserved_space (`int`): Space to reserve for user files, in MB.
            database_space (`int`): Space to reserve for database files, in MB.
            fat32 (`bool`): Whether the filesystem should be formatted as fat32
                 (defaults to `True`)

        .. versionchanged:: 1.9
           Will now reopen the internal handle if the log is mounted in order
           to refresh `Memorator.log.ldf_version`

        """
        filesystem = int(fat32)
        dll.kvmDeviceFormatDisk(self.handle, int(filesystem), int(reserved_space), database_space)
        if self.mounted:
            self.reopen(device_type=self.device_type, mount=self.mounted)

    def read_config(self):
        """Read the configuration of the Memorator

        The configuration is returned as a `bytes` object with the binary
        configuration data (param.lif).

        If a `.kvamemolibxml.Configuration` is desired, the returned `bytes` can
        be parsed using `.kvamemolibxml.load_lif`::

            config_object = kvamemolibxml.load_lif(memorator.read_config())

        """
        buf, actual_len = self._try_read_config(self._ASSUMED_CONFIG_SIZE)
        if actual_len.value > len(buf):
            buf, actual_len = self._try_read_config(actual_len.value)
        config = buf.raw[: actual_len.value]
        assert len(config) == actual_len.value
        return config

    def reopen(self, device_type=None, mount=False):
        """Closes and then reopens the internal handle"""
        self.__del__()
        if device_type is None:
            device_type = self.device_type
        handle = _openDevice(self.channel_number, device_type)
        self.__init__(handle, self.channel_number, device_type)
        if mount:
            self.mount()

    def _try_read_config(self, length):
        buf = (ct.c_char * length)()
        actual_len = ct.c_size_t()
        dll.kvmKmfReadConfig(self.handle, ct.byref(buf), ct.sizeof(buf), ct.byref(actual_len))

        return buf, actual_len

    def write_config(self, config_lif):
        """Writes configuration to the Memorator

        The configuration should be given as a `bytes` object with the binary
        configuration data (param.lif).

        Given a `.kvamemolibxml.Configuration` object, pass its `lif`
        attribute to this function::

            memorator.write_config(config_object.lif)

        """
        buf = ct.create_string_buffer(config_lif, len(config_lif))
        dll.kvmKmfWriteConfig(self.handle, ct.byref(buf), ct.sizeof(buf))

    def _get_software_info(self, itemcode):
        itemcode = ct.c_int32(itemcode)
        major = ct.c_uint()
        minor = ct.c_uint()
        build = ct.c_uint()
        flags = ct.c_uint()  # "for internal use only" => ignored

        dll.kvmDeviceGetSoftwareInfo(
            self.handle,
            itemcode,
            ct.byref(major),
            ct.byref(minor),
            ct.byref(build),
            ct.byref(flags),
        )

        return VersionNumber(major.value, minor.value, build.value)
