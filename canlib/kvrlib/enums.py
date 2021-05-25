from ..cenum import CEnum, CFlag


class DeviceUsage(CEnum):
    """kvrDeviceUsage_xxx

    Remote device usage status.
    """

    UNKNOWN = 0
    FREE = 1
    REMOTE = 2
    USB = 3
    CONFIG = 4


class Accessibility(CEnum):
    """kvrAccessibility_xxx

    Remote device accessability status.
    """

    UNKNOWN = 0
    PUBLIC = 1
    PROTECTED = 2
    PRIVATE = 3


class Availability(CFlag):
    """kvrAvailability_xxx

    Device avalability flags.
    """

    NONE = 0x0
    FOUND_BY_SCAN = 0x1
    STORED = 0x2


class ConfigMode(CEnum):
    """kvrConfigMode_xxx

    Configuration mode.
    """

    R = 0
    RW = 1
    ERASE = 2


class Error(CEnum):
    NOT_INITIALIZED = -1
    GENERIC = -2
    CHECKSUM = -3
    PARAMETER = -4
    PASSWORD = -5
    BLANK = -6
    NO_DEVICE = -7
    NO_ANSWER = -8
    NOT_IMPLEMENTED = -9
    PERMISSION_DENIED = -10
    OUT_OF_SPACE = -11
    NO_SERVICE = -12
    DUPLICATED_DEVICE = -13
    XML_VALIDATION = -14
    BUFFER_TOO_SMALL = -15


class NetworkState(CEnum):
    """kvrNetworkState_xxx

    States for network connection.
    """

    UNKNOWN = 0
    INVALID = 1
    STARTUP = 2
    INITIALIZING = 3
    NOT_CONNECTED = 4
    CONNECTION_DELAY = 5
    CONNECTING = 6
    CONNECTED = 7
    AUTHENTICATING = 8
    AUTHENTICATION_FAILED = 9
    ONLINE = 10
    FAILED_MIC = 11


class BasicServiceSet(CEnum):
    """kvrBss_xxx

    Basic Service Set.
    """

    INFRASTRUCTURE = 0
    INDEPENDENT = 1
    ANY = 2


class RegulatoryDomain(CEnum):
    """kvrRegulatoryDomain_xxx

    Regulatory domain.
    """

    JAPAN_TELEC = 0
    EUROPE_ETSI = 1
    NORTH_AMERICA_FCC = 2
    WORLD = 3
    CHINA_MII = 4


class RemoteState(CEnum):
    """kvrRemoteState_xxx

    State of connection to device.
    """

    VOID = 0
    AVAILABLE = 1
    DISCOVERED = 2
    STARTING = 3
    STARTED = 4
    CONNECTION_DOWN = 5
    CONNECTION_UP = 6
    REDISCOVER = 7
    UNWILLING = 8
    REDISCOVER_PENDING = 9
    CLOSING = 10
    REMOVE_ME = 11
    STANDBY = 12
    CONFIG_CHANGED = 13
    STOPPING = 14
    INSTALLING = 15


class AddressType(CEnum):
    """kvrAddressType_xxx

    Type of device address.

    Note:
        Ports are currently not used.
    """

    UNKNOWN = 0
    IPV4 = 1
    IPV6 = 2
    IPV4_PORT = 3
    MAC = 4


class AddressTypeFlag(CFlag):
    """kvrAddressTypeFlag_xxx

    Flags for setting what addresses that should be returned by
    ``kvrDiscoveryGetDefaultAddresses()``.

    """

    ALL = 0xFF
    BROADCAST = 0x01
    STORED = 0x02


class ServiceState(CEnum):
    """kvrServiceState_xxx

    Current service state.
    """

    VOID = 0
    AVAILABLE = 1
    DISCOVERED = 2
    STARTING = 3
    STARTED = 4
    CONNECTION_DOWN = 5
    CONNECTION_UP = 6
    REDISCOVER = 7
    UNWILLING = 8
    REDISCOVER_PENDING = 9
    CLOSING = 10
    REMOVE_ME = 11
    STANDBY = 12
    CONFIG_CHANGED = 13
    STOPPING = 14
    INSTALLING = 15


class StartInfo(CEnum):
    """kvrStartInfo_xxx

    Current start information.
    """

    NONE = 0
    START_OK = 1
    ERR_IN_USE = 2
    ERR_PWD = 3
    ERR_NOTME = 4
    ERR_CONFIGURING = 5
    ERR_PARAM = 6
    ERR_ENCRYPTION_PWD = 7
