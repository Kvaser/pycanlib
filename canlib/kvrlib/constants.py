from . import enums

# Most of these constants are deprecated, use the enum mentioned instead. (Or
# whatever is after the '=', even if its not an enum.)

kvrOK = 0
kvrERR_NOT_INITIALIZED = enums.Error.NOT_INITIALIZED
kvrERR_GENERIC = enums.Error.GENERIC
kvrERR_CHECKSUM = enums.Error.CHECKSUM
kvrERR_PARAMETER = enums.Error.PARAMETER
kvrERR_PASSWORD = enums.Error.PASSWORD
kvrERR_BLANK = enums.Error.BLANK
kvrERR_NO_DEVICE = enums.Error.NO_DEVICE
kvrERR_NO_ANSWER = enums.Error.NO_ANSWER
kvrERR_NOT_IMPLEMENTED = enums.Error.NOT_IMPLEMENTED
kvrERR_PERMISSION_DENIED = enums.Error.PERMISSION_DENIED
kvrERR_OUT_OF_SPACE = enums.Error.OUT_OF_SPACE
kvrERR_NO_SERVICE = enums.Error.NO_SERVICE
kvrERR_DUPLICATED_DEVICE = enums.Error.DUPLICATED_DEVICE
kvrERR_XML_VALIDATION = enums.Error.XML_VALIDATION

kvrNetworkState_UNKNOWN = enums.NetworkState.UNKNOWN
kvrNetworkState_INVALID = enums.NetworkState.INVALID
kvrNetworkState_STARTUP = enums.NetworkState.STARTUP
kvrNetworkState_INITIALIZING = enums.NetworkState.INITIALIZING
kvrNetworkState_NOT_CONNECTED = enums.NetworkState.NOT_CONNECTED
kvrNetworkState_CONNECTION_DELAY = enums.NetworkState.CONNECTION_DELAY
kvrNetworkState_CONNECTING = enums.NetworkState.CONNECTING
kvrNetworkState_CONNECTED = enums.NetworkState.CONNECTED
kvrNetworkState_AUTHENTICATING = enums.NetworkState.AUTHENTICATING
kvrNetworkState_AUTHENTICATION_FAILED = enums.NetworkState.AUTHENTICATION_FAILED
kvrNetworkState_ONLINE = enums.NetworkState.ONLINE
kvrNetworkState_FAILED_MIC = enums.NetworkState.FAILED_MIC

kvrBss_INFRASTRUCTURE = enums.BasicServiceSet.INFRASTRUCTURE
kvrBss_INDEPENDENT = enums.BasicServiceSet.INDEPENDENT
kvrBss_ANY = enums.BasicServiceSet.ANY

kvrRegulatoryDomain_JAPAN_TELEC = enums.RegulatoryDomain.JAPAN_TELEC
kvrRegulatoryDomain_EUROPE_ETSI = enums.RegulatoryDomain.EUROPE_ETSI
kvrRegulatoryDomain_NORTH_AMERICA_FCC = enums.RegulatoryDomain.NORTH_AMERICA_FCC
kvrRegulatoryDomain_WORLD = enums.RegulatoryDomain.WORLD
kvrRegulatoryDomain_CHINA_MII = enums.RegulatoryDomain.CHINA_MII

kvrRemoteState_VOID = enums.RemoteState.VOID
kvrRemoteState_AVAILABLE = enums.RemoteState.AVAILABLE
kvrRemoteState_DISCOVERED = enums.RemoteState.DISCOVERED
kvrRemoteState_STARTING = enums.RemoteState.STARTING
kvrRemoteState_STARTED = enums.RemoteState.STARTED
kvrRemoteState_CONNECTION_DOWN = enums.RemoteState.CONNECTION_DOWN
kvrRemoteState_CONNECTION_UP = enums.RemoteState.CONNECTION_UP
kvrRemoteState_REDISCOVER = enums.RemoteState.REDISCOVER
kvrRemoteState_UNWILLING = enums.RemoteState.UNWILLING
kvrRemoteState_REDISCOVER_PENDING = enums.RemoteState.REDISCOVER_PENDING
kvrRemoteState_CLOSING = enums.RemoteState.CLOSING
kvrRemoteState_REMOVE_ME = enums.RemoteState.REMOVE_ME
kvrRemoteState_STANDBY = enums.RemoteState.STANDBY
kvrRemoteState_CONFIG_CHANGED = enums.RemoteState.CONFIG_CHANGED
kvrRemoteState_STOPPING = enums.RemoteState.STOPPING
kvrRemoteState_INSTALLING = enums.RemoteState.INSTALLING

kvrAddressTypeFlag_ALL = enums.AddressTypeFlag.ALL
kvrAddressTypeFlag_BROADCAST = enums.AddressTypeFlag.BROADCAST
kvrAddressTypeFlag_STORED = enums.AddressTypeFlag.STORED

kvrServiceState_VOID = enums.ServiceState.VOID
kvrServiceState_AVAILABLE = enums.ServiceState.AVAILABLE
kvrServiceState_DISCOVERED = enums.ServiceState.DISCOVERED
kvrServiceState_STARTING = enums.ServiceState.STARTING
kvrServiceState_STARTED = enums.ServiceState.STARTED
kvrServiceState_CONNECTION_DOWN = enums.ServiceState.CONNECTION_DOWN
kvrServiceState_CONNECTION_UP = enums.ServiceState.CONNECTION_UP
kvrServiceState_REDISCOVER = enums.ServiceState.REDISCOVER
kvrServiceState_UNWILLING = enums.ServiceState.UNWILLING
kvrServiceState_REDISCOVER_PENDING = enums.ServiceState.REDISCOVER_PENDING
kvrServiceState_CLOSING = enums.ServiceState.CLOSING
kvrServiceState_REMOVE_ME = enums.ServiceState.REMOVE_ME
kvrServiceState_STANDBY = enums.ServiceState.STANDBY
kvrServiceState_CONFIG_CHANGED = enums.ServiceState.CONFIG_CHANGED
kvrServiceState_STOPPING = enums.ServiceState.STOPPING
kvrServiceState_INSTALLING = enums.ServiceState.INSTALLING

kvrStartInfo_NONE = enums.StartInfo.NONE
kvrStartInfo_START_OK = enums.StartInfo.START_OK
kvrStartInfo_ERR_IN_USE = enums.StartInfo.ERR_IN_USE
kvrStartInfo_ERR_PWD = enums.StartInfo.ERR_PWD
kvrStartInfo_ERR_NOTME = enums.StartInfo.ERR_NOTME
kvrStartInfo_ERR_CONFIGURING = enums.StartInfo.ERR_CONFIGURING
kvrStartInfo_ERR_PARAM = enums.StartInfo.ERR_PARAM
kvrStartInfo_ERR_ENCRYPTION_PWD = enums.StartInfo.ERR_ENCRYPTION_PWD
