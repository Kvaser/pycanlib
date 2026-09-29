import re
import time
import traceback

from . import canlib, deprecation, kvMemoConfig, kvmlib
from .exceptions import CanlibException


class kvDevice:
    """Holds information about a Kvaser CAN device

    Args:
        ch (int): CANlib channel where the device is currently connected.
        flags (int): Optional flags such as canlib.canOPEN_EXCLUSIVE.
        canlibHnd : Optional canlib.canlib object, usually creates a new one.
        ean (str): EAN for the device, e.g. "73-30130-00778-9". Used instead of
            ch.
        serial (str): Optional serial number of the device, can be used in
            conjuntion with ean.
        cardChannel (int): Optional local channel on card, can be used in
            conjunction with ean.

    .. deprecated:: 1.9
       Use `canlib.Device` instead.

    """

    # ean:    73-30130-00671-3
    # ean_hi: 73301
    # ean_lo: 30006713

    @staticmethod
    def ean2ean_hi(ean):
        eanCompact = re.sub('-', '', ean)
        match = re.match(r'(\d{5})(\d{8})', eanCompact)
        return int('0x%s' % match.group(1), 0)

    @staticmethod
    def ean2ean_lo(ean):
        eanCompact = re.sub('-', '', ean)
        match = re.match(r'(\d{5})(\d{8})', eanCompact)
        return int('0x%s' % match.group(2), 0)

    @staticmethod
    def ean_hi_lo2ean(ean_hi, ean_lo):
        return "{:02x}-{:05x}-{:05x}-{:x}".format(
            ean_hi >> 12,
            ((ean_hi & 0xFFF) << 8) | (ean_lo >> 24),
            (ean_lo >> 4) & 0xFFFFF,
            ean_lo & 0xF,
        )

    @staticmethod
    def allDevices(reinitialize=True):
        devices = []
        indx = -1
        if reinitialize:
            canlib.reinitializeLibrary()
        for ch in range(canlib.getNumberOfChannels()):
            try:
                dev = kvDevice(ch=ch)
            except canlib.canError as e:
                if e.status == canlib.canERR_NOTFOUND:
                    return devices
                else:
                    raise e
            if indx == -1 or dev != devices[indx]:
                devices.append(dev)
                indx += 1
        return devices

    def __init__(self, ch=None, flags=0, canlibHnd=None, ean=None, serial=None, cardChannel=0):
        deprecation.manual_warn(
            "The kvDevice class has been deprecated, use canlib.Device instead"
        )
        self._cardChannel = cardChannel
        if ch is None and (ean is not None or serial is not None):
            ch = self._findChannel(ean, serial, cardChannel)

        if ch is not None:
            self.channel = canlib.openChannel(ch, flags)
            self._loadInfo()
            self.close()
        else:
            self.channel = None
            self._loadInfo()
            self._ean = ean
            self._serial = serial
        self._channel = ch
        self.noOfChannels = None
        self.memo = None

    def _loadInfo(self):
        if self.channel is not None:
            self._card = self.cardNumber()
            self._name = self.name()
            self._ean = self.ean()
            self._serial = self.serial()
            self._fw = self.fw()
            self._driver = self.driverName()
            self._defaultHostname = self.defaultHostname()
            self._cardChannel = self.cardChannel()
        else:
            self.channel = None
            self._card = None
            self._name = None
            self._ean = None
            self._serial = None
            self._fw = None
            self._driver = None
            self._defaultHostname = None

    def memoOpenEx(self):
        # Deprecated, use memoOpen() instead.
        self.memoOpen()

    def memoOpen(self, deviceType=kvmlib.kvmDEVICE_MHYDRA_EXT):
        self.memo = kvmlib.kvmlib()
        self.memo.deviceOpen(memoNr=self._card, devicetype=deviceType)

    def memoClose(self):
        self.memo.close()
        self.memo = None

    def readConfig(self):
        memoWasClosed = False
        if self.memo is None:
            memoWasClosed = True
            self.memoOpen()
        self.config = kvMemoConfig.kvMemoConfig(param_lif=self.memo.kmfReadConfig())
        if memoWasClosed:
            self.memoClose()
        return self.config

    def writeConfig(self, config=None):
        if config is not None:
            self.config = config
        memoWasClosed = False
        if self.memo is None:
            memoWasClosed = True
            self.memoOpen()
        self.memo.writeConfig(self.config)
        if memoWasClosed:
            self.memoClose()

    def memoReadEvents(self, fileIndx):
        self.memo.logFileMount(fileIndx)
        memoEvents = self.memo.logFileReadEvents()
        self.memo.logFileDismount()
        return memoEvents

    def lastKnowncanlibChannel(self):
        return self._channel

    def cardNumber(self):
        return self.channel.getChannelData_CardNumber()

    def cardChannels(self):
        return self.noOfChannels

    def cardChannel(self):
        """Read card channel number from device

        Returns:
            cardChannel (int): The local channel on card, first channel is
            number 0.
        """
        return self.channel.getChannelData_Chan_No_On_Card()

    def close(self):
        try:
            self.channel.close()
        except canlib.canError as e:
            # qqqmac call warn() instead.
            print("WARNING: Failed to close, ", e)
            traceback.print_stack(limit=2)
        self.channel = None

    def driverName(self):
        return self.channel.getChannelData_DriverName()

    def ean(self):
        return self.channel.getChannelData_EAN()

    def fw(self):
        (major, minor, build) = self.channel.getChannelData_Firmware()
        return (major, minor, build)

    def name(self):
        return self.channel.getChannelData_Name()

    def serial(self):
        return self.channel.getChannelData_Serial()

    def setModeVirtualLogger(self):
        # kvDeviceSetMode fails silently if it doesn't support the given device
        # mode
        self.channel.kvDeviceSetMode(canlib.kvDEVICE_MODE_LOGGER)
        if self.channel.kvDeviceGetMode() != canlib.kvDEVICE_MODE_LOGGER:
            raise CanlibException(
                "Could not set device in virtual logger mode. Is CAN power applied?."
            )

    def setModeNormal(self):
        # kvDeviceSetMode fails silently if it doesn't support the given device
        # mode
        self.channel.kvDeviceSetMode(canlib.kvDEVICE_MODE_INTERFACE)
        if self.channel.kvDeviceGetMode() != canlib.kvDEVICE_MODE_INTERFACE:
            raise CanlibException("Could not set device in normal mode.")

    def defaultHostname(self):
        ean_part = '%x' % kvDevice.ean2ean_lo(self._ean)
        return 'kv-%s-%06d' % (ean_part[-5:], self._serial)

    def hasScript(self):
        if (
            self._ean == '73-30130-00567-9'
            or self._ean == '73-30130-00778-9'
            or self._ean == '73-30130-00821-2'
            or self._ean == '73-30130-00819-9'
            or self._ean == '73-30130-00752-9'
            or self._ean == '73-30130-00779-6'
        ):
            return True
        else:
            return False

    def isLogger(self):
        if (
            self._ean == '73-30130-00567-9'
            or self._ean == '73-30130-00778-9'
            or self._ean == '73-30130-00821-2'
            or self._ean == '73-30130-00819-9'
        ):
            return True
        else:
            return False

    def open(self, flags=0, timeout=10, unloadCanlib=False):
        if self.channel is not None:
            self.close()
        startTime = time.time()
        while True:
            ch = self._findChannel(
                self._ean, self._serial, self._cardChannel, unloadCanlib=unloadCanlib
            )
            if ch is not None:
                self.channel = canlib.openChannel(ch, flags)
                self._channel = ch
                self._loadInfo()

            if self.channel is None:
                print(
                    'Waiting for device %s %s. Slept %ds (timeout:%d)'
                    % (self._ean, self._serial, time.time() - startTime, timeout)
                )
                time.sleep(2)
            if (not (self.channel is None)) or ((time.time() - startTime) > timeout):
                break
        if self.channel is None:
            raise CanlibException(
                f"Could not find device {self._ean} {self._serial} (timeout: {timeout} s)."
            )

    def write(self, frame):
        """Write a CAN message to the bus.

        Args:
            frame (canlib.frame.Frame): The data frame to be sent
        """
        self.channel.write(frame)

    def writeWait(self, frame, timeout):
        """Write a CAN message to the bus.

        Args:
            message (canlib.frame.Frame): The data frame to send
        """
        self.channel.writeWait(frame, timeout)

    def _findChannel(self, wanted_ean, wanted_serial=None, card_channel=0, unloadCanlib=False):
        channel = None
        if unloadCanlib:
            canlib.reinitializeLibrary()
        else:
            canlib.initializeLibrary()
        for ch in range(canlib.getNumberOfChannels()):
            try:
                ean = canlib.getChannelData_EAN(ch)
                serial = canlib.getChannelData_Serial(ch)
                c_channel = canlib.getChannelData_Chan_No_On_Card(ch)
            except canlib.canError as e:
                if e.status == canlib.canERR_NOCARD:
                    print('Card was removed')
                    break
                else:
                    raise e
            if (
                (ean == wanted_ean or wanted_ean is None)
                and (c_channel == card_channel)
                and ((serial == wanted_serial) or (wanted_serial is None))
            ):
                channel = ch
                break
        return channel

    def _waitToDisappear(self, timeout=10):
        startTime = time.time()
        print('Wait for disappear...', end="")
        while (
            self._findChannel(self._ean, self._serial, self._cardChannel, unloadCanlib=True)
            is not None
        ):
            if time.time() - startTime > timeout:
                print(
                    "\nWARNING: Timeout (%s s) reached while waiting for"
                    " device (ean:%s, sn:%s) to disappear!" % (timeout, self._ean, self._serial)
                )
                print('I will keep running and assume that I was too slow...')
                return
            time.sleep(1)
            print('.\n', end="")

    # required in Python 2
    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        if other is None:
            return False
        if self._ean == other._ean and self._serial == other._serial:
            return True
        else:
            if (self._serial is None or other._serial is None) and self._ean == other._ean:
                return True
            else:
                return False

    def __hash__(self):
        return hash(f"{self._ean} {self._serial}")

    def __str__(self):
        text = f'Device: {self._name}\n'
        text = text + f'EAN           : {self._ean}\n'
        text = text + f'S/N           : {self._serial}\n'
        if self._fw is not None:
            fwVersion = "v%d.%d.%d" % self._fw
        else:
            fwVersion = "None"
        text = text + f'FW            : {fwVersion}\n'
        text = text + f'Card          : {self._card}\n'
        text = text + f'Drv           : {self._driver}\n'
        text = text + f'Card channel  : {self._cardChannel}\n'
        text = text + f'Canlib channel: {self._channel}\n'
        return text


if __name__ == '__main__':
    devices = kvDevice.allDevices()
    print(f"List all {len(devices)} devices...")
    for dev in devices:
        print("\n", dev)
