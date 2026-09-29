"""Wrapper for the Kvaser CANlib library

At the core of canlib you have functions to set bus parameters (e.g. bit rate),
go bus on/off and read/write CAN messages. You can also use CANlib to download
and start t programs on your device. All of this is done on a device that is
attached to your computer, and they are universally available across all
supported Kvaser Devices. If you can see your device listed in the Kvaser
Hardware tool, it is connected and you can communicate with it through CANlib.

"""

from ._channel import canChannel
from .channel import Channel, ScriptText, openChannel
from .channeldata import ChannelData, HandleData
from .constants import *
from .enums import (AcceptFilterFlag, Bitrate, BitrateFD, BusTypeGroup,
                    ChannelCap, ChannelCapEx, ChannelDataItem, ChannelFlags,
                    DeviceMode, Driver, DriverCap, EnvVarType, Error,
                    HardwareType, IOControlItem, LEDAction, LoggerType,
                    MessageFlag, Notify, Open, OperationalMode, RemoteType,
                    ScriptRequest, ScriptStatus, ScriptStop, Stat,
                    TransceiverType, TxeDataItem)
from .envvar import EnvVar  # for backwards-compatibility
from .envvar import EnvVar as envvar
from .exceptions import (CanError, CanNoMsg, CanNotFound, CanScriptFail,
                         CanTimeout, CanOutOfMemory, CanInvalidHandle,
                         EnvvarException, EnvvarNameError, EnvvarValueError,
                         IoNoValidConfiguration,
                         IoPinConfigurationNotConfirmed, TxeFileIsEncrypted)
from .iocontrol import IOControl
from .txe import SourceElement, Txe
from .wrapper import CANLib  # for backwards-compatibility
from .wrapper import CANLib as canlib
from .wrapper import (  # deprecated
    ChannelData_Channel_Flags, ChannelData_Channel_Flags_bits, dllversion,
    enumerate_hardware, getChannelData_CardNumber,
    getChannelData_Chan_No_On_Card, getChannelData_Channel_Flags,
    getChannelData_Cust_Name, getChannelData_DriverName, getChannelData_EAN,
    getChannelData_EAN_short, getChannelData_Firmware, getChannelData_Name,
    getChannelData_Serial, getErrorText, getNumberOfChannels, getVersion,
    initializeLibrary, prodversion, reinitializeLibrary, translateBaud,
    unloadLibrary)
from .timedomain import TimeDomain, TimeDomainData
canError = CanError
canNoMsg = CanNoMsg
canScriptFail = CanScriptFail
