import ctypes as ct

from .enums import Accessibility, Availability, DeviceUsage


class kvrVersion(ct.Structure):
    _fields_ = [
        ("minor", ct.c_uint8),
        ("major", ct.c_uint8),
    ]

    def __str__(self):
        return "%d.%d" % (self.major, self.minor)


class kvrAddress(ct.Structure):
    Type_UNKNOWN = 0
    Type_IPV4 = 1
    Type_IPV6 = 2
    Type_IPV4_PORT = 3
    Type_MAC = 4

    TypeText = {
        Type_UNKNOWN: 'UNKNOWN',
        Type_IPV4: 'IPV4',
        Type_IPV6: 'IPV6',
        Type_IPV4_PORT: 'IPV4_PORT',
        Type_MAC: 'MAC',
    }

    _fields_ = [("type", ct.c_uint), ("address", ct.c_ubyte * 20)]

    def __str__(self):
        addr = '-'
        if self.type == self.Type_IPV4:
            addr = '.'.join(str(x) for x in self.address[:4])
        elif self.type == self.Type_IPV4_PORT:
            addr = '.'.join(str(x) for x in self.address[:4])
            addr += ':%s' % self.address[5]
        type = self.TypeText[self.type]
        return "%s (%s)" % (addr, type)


class kvrAddressList(ct.Structure):
    _fields_ = [('elements', ct.c_short), ('STRUCT_ARRAY', ct.POINTER(kvrAddress))]

    def __init__(self, num_of_structs=20):
        elems = (kvrAddress * num_of_structs)()
        self.STRUCT_ARRAY = ct.cast(elems, ct.POINTER(kvrAddress))
        self.elements = num_of_structs
        self.count = 0

    def __str__(self):
        elements = []
        for i in range(0, self.count):
            elements.append("%s" % self.STRUCT_ARRAY[i])
        return "\n".join(elements)


class kvrCipherInfoElement(ct.Structure):
    _fields_ = [
        ("version", ct.c_uint32),
        ("capability", ct.c_uint32),
        ("group_cipher", ct.c_uint32),
        ("list_cipher_auth", ct.c_uint32),
    ]


class kvrDeviceInfo(ct.Structure):
    _fields_ = [
        ("struct_size", ct.c_uint32),
        ("ean_hi", ct.c_uint32),
        ("ean_lo", ct.c_uint32),
        ("ser_no", ct.c_uint32),
        ("fw_major_ver", ct.c_int32),
        ("fw_minor_ver", ct.c_int32),
        ("fw_build_ver", ct.c_int32),
        ("name", ct.c_char * 256),
        ("host_name", ct.c_char * 256),
        ("usage", ct.c_int32),
        ("accessibility", ct.c_int32),
        ("accessibility_pwd", ct.c_char * 256),
        ("device_address", kvrAddress),
        ("client_address", kvrAddress),
        ("base_station_id", kvrAddress),
        ("request_connection", ct.c_int32),
        ("availability", ct.c_int32),
        ("encryption_key", ct.c_char * 32),
        ("reserved1", ct.c_char * 256),
        ("reserved2", ct.c_char * 256),
    ]

    def connect(self):
        self.request_connection = 1

    def disconnect(self):
        self.request_connection = 0

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        if other is None:
            return False
        if (
            self.ean_hi == other.ean_hi
            and self.ean_lo == other.ean_lo
            and self.ser_no == other.ser_no
        ):
            return True
        else:
            return False

    def __hash__(self):
        return hash("%x %x %d" % (self.ean_hi, self.ean_lo, self.ser_no))

    def __str__(self):
        text = "\n"
        acc_pwd = "no"
        enc_key = "no"

        text += "name/hostname  : \"%s\" / \"%s\"\n" % (
            self.name.decode(),
            self.host_name.decode(),
        )
        text += "  ean/serial   : %x-%x / %d\n" % (self.ean_hi, self.ean_lo, self.ser_no)
        text += "  fw           : %d.%d.%03d\n" % (
            self.fw_major_ver,
            self.fw_minor_ver,
            self.fw_build_ver,
        )
        text += "  addr/cli/AP  : %s / %s / %s\n" % (
            self.device_address,
            self.client_address,
            self.base_station_id,
        )
        text += "  availability : %s\n" % (Availability(self.availability))
        text += "  usage/access : %s / %s\n" % (
            DeviceUsage(self.usage),
            Accessibility(self.accessibility),
        )
        if self.accessibility_pwd:
            acc_pwd = "yes"
        if self.encryption_key:
            enc_key = "yes"
        text += "  pass/enc.key : %s / %s" % (acc_pwd, enc_key)
        return text

    def __repr__(self):
        return self.__str__()


class kvrDeviceInfoList(ct.Structure):
    _fields_ = [('elements', ct.c_short), ('STRUCT_ARRAY', ct.POINTER(kvrDeviceInfo))]

    def __init__(self, deviceInfos):
        num_of_structs = len(deviceInfos)
        elems = (kvrDeviceInfo * num_of_structs)()
        self.STRUCT_ARRAY = ct.cast(elems, ct.POINTER(kvrDeviceInfo))

        for elem in range(0, num_of_structs):
            self.STRUCT_ARRAY[elem] = deviceInfos[elem]
        self.elements = num_of_structs
        self.count = 0

    def __str__(self):
        elements = []
        for i in range(0, self.elements):
            elements.append("%s" % (self.STRUCT_ARRAY[i]))
        return "\n".join(elements)
