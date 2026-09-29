from ..cenum import CEnum, CFlag


class DeviceUsage(CEnum):
    """kvrDeviceUsage_xxx

    Remote device usage status.
    """

    UNKNOWN = 0  #: Unknown (e.g., no reply from device).
    FREE = 1  #: Not in use.
    REMOTE = 2  #: Connected to a PC (as a remote device).
    USB = 3  #: Connected via USB cable.
    CONFIG = 4  #: Device is being configured via USB.


class Accessibility(CEnum):
    """kvrAccessibility_xxx

    Remote device accessability status.
    """

    UNKNOWN = 0  #: Unknown (e.g., no reply from device).
    PUBLIC = 1  #: Public (visible for all, no password required to connect).
    PROTECTED = 2  #: Protected (visible for all, password needed to connect).
    PRIVATE = 3  #: Private (invisible, password needed to connect).


class Availability(CFlag):
    """kvrAvailability_xxx

    Device avalability flags.
    """

    NONE = 0x0  #: Manually added.
    FOUND_BY_SCAN = 0x1  #: Device was found by scan.
    STORED = 0x2  #: Device was stored.


class ConfigMode(CEnum):
    """kvrConfigMode_xxx

    Configuration mode.
    """

    R = 0  #: Read only.
    RW = 1  #: Read/write.
    ERASE = 2  #: Erase and write.


class Error(CEnum):
    OK = 0  #: OK!
    NOT_INITIALIZED = -1  #: kvrlib has not been initialized.
    GENERIC = -2  #: Generic error.
    CHECKSUM = -3  #: Checksum problem.
    PARAMETER = -4  #: Error in supplied in parameters.
    PASSWORD = -5  #: Supplied password was wrong.
    BLANK = -6  #: List was not set or no more results.
    NO_DEVICE = -7  #: Remote device is unreachable.
    NO_ANSWER = -8  #: No answer arrived within given timeout.
    NOT_IMPLEMENTED = -9  #: Function is not yet implemented.
    PERMISSION_DENIED = -10  #: Permission denied.
    OUT_OF_SPACE = -11  #: Out of space, eg. to many open handles, to small buffer.
    NO_SERVICE = -12  #: The helper service is not running.
    DUPLICATED_DEVICE = -13  #: There are duplicates in the device list.
    XML_VALIDATION = -14  #: XML-file validation failed.
    BUFFER_TOO_SMALL = -15  #: The buffer provided was not large enough to contain the requested data.


class NetworkState(CEnum):
    """kvrNetworkState_xxx

    States for network connection.
    """

    UNKNOWN = 0  #: Bad state, should never be reported.
    INVALID = 1  #: Network hardware has been disabled.
    STARTUP = 2  #: Configuring network hardware.
    INITIALIZING = 3  #: Started, waiting for initialization.
    NOT_CONNECTED = 4  #: No connection (may auto-connect).
    CONNECTION_DELAY = 5  #: Delay during connection (ad-hoc).
    CONNECTING = 6  #: Waiting for connections (ad-hoc).
    CONNECTED = 7  #: Network is reached.
    AUTHENTICATING = 8  #: EAPOL handshake ongoing.
    AUTHENTICATION_FAILED = 9  #: Authentication have failed.
    ONLINE = 10  #: Authentication completed.
    FAILED_MIC = 11  #: MIC verification (EAPOL-key) failed.


class BasicServiceSet(CEnum):
    """kvrBss_xxx

    Basic Service Set.
    """

    INFRASTRUCTURE = 0  #: Network with AP.
    INDEPENDENT = 1  #: Ad-hoc network.
    ANY = 2  #: Any.


class RegulatoryDomain(CEnum):
    """kvrRegulatoryDomain_xxx

    Regulatory domain.
    """

    JAPAN_TELEC = 0  #: TELEC
    EUROPE_ETSI = 1  #: ETSI
    NORTH_AMERICA_FCC = 2  #: FCC
    WORLD = 3  #: WORLD
    CHINA_MII = 4  #: MII


class RemoteState(CEnum):
    """kvrRemoteState_xxx

    State of connection to device.
    """

    VOID = 0  #: Marked as not in list.
    AVAILABLE = 1  #: Tries to ping known device.
    DISCOVERED = 2  #: Currently not used.
    STARTING = 3  #: Initializes for new device.
    STARTED = 4  #: Currently not used.
    CONNECTION_DOWN = 5  #: Will try and restore connection.
    CONNECTION_UP = 6  #: Device connected, heartbeat up.
    REDISCOVER = 7  #: Trying to talk to device.
    UNWILLING = 8  #: Device turned down connection req.
    REDISCOVER_PENDING = 9  #: Will do rediscover in a moment.
    CLOSING = 10  #: Will stop communication.
    REMOVE_ME = 11  #: Device removed, it will be stopped.
    STANDBY = 12  #: Known device, but unused.
    CONFIG_CHANGED = 13  #: Same as UNWILLING.
    STOPPING = 14  #: Tries to stop device.
    INSTALLING = 15  #: Driver installation is in progress.


class AddressType(CEnum):
    """kvrAddressType_xxx

    Type of device address.

    Note:
        Ports are currently not used.
    """

    UNKNOWN = 0  #: Unknown (e.g., no reply from device).
    IPV4 = 1  #: IP v.4 address.
    IPV6 = 2  #: IP v.6 address.
    IPV4_PORT = 3  #: IP v.4 address with tcp-port.
    MAC = 4  #: Ethernet MAC address.


class AddressTypeFlag(CFlag):
    """kvrAddressTypeFlag_xxx

    Flags for setting what addresses that should be returned by
    `get_default_discovery_addresses`.

    """

    ALL = 0xFF  #: All defined below
    BROADCAST = 0x01  #: Broadcast addresses
    STORED = 0x02  #: Previously stored addresses


class ServiceState(CEnum):
    """kvrServiceState_xxx

    Current service state.
    """

    VOID = 0  #: Void
    AVAILABLE = 1  #: Device available
    DISCOVERED = 2  #: Device discovered
    STARTING = 3  #: Device is starting, other devices may inhibit this device from being started at the moment (e.g. by installing).
    STARTED = 4  #: Device is started
    CONNECTION_DOWN = 5  #: Connection is currently down
    CONNECTION_UP = 6  #: Connection is corrently up. The device should be showing up in Kvaser  Hardware and be ready to be used from CANlib.
    REDISCOVER = 7  #: We've lost the device - rediscover it
    UNWILLING = 8  #: Unwilling, see sub state for reason
    REDISCOVER_PENDING = 9  #: Rediscover is pending
    CLOSING = 10  #: Closing device
    REMOVE_ME = 11  #: Removing the device
    STANDBY = 12  #: Standby, the service is not taking any actions against this device
    CONFIG_CHANGED = 13  #: Configuration has changed
    STOPPING = 14  #: Stopping devic
    INSTALLING = 15  #: Device is currently being installed


class StartInfo(CEnum):
    """kvrStartInfo_xxx

    Current start information.
    """

    NONE = 0  #: No information available
    START_OK = 1  #: Started OK
    ERR_IN_USE = 2  #: Already connected to someone else
    ERR_PWD = 3  #: Wrong connection pwd
    ERR_NOTME = 4  #: This start is not for me
    ERR_CONFIGURING = 5  #: I'm being configured so won't start
    ERR_PARAM = 6  #: Invalid parameters in QRV (non matching versions)
    ERR_ENCRYPTION_PWD = 7  #: Wrong encryption password.
