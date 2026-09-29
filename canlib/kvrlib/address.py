from collections import namedtuple

from .enums import AddressType
from .structures import kvrAddress


class Address(namedtuple('_Address', "type address")):
    """An IP or MAC address

    Args:
        type (`~canlib.kvrlib.AddressType`): Address type.
        address (`list[int]`): A list of integers, the numbers in the address.

    """

    @classmethod
    def from_c(cls, c_addr):
        """Create an `Address` object from a `~canlib.kvrlib.kvrAddress` object"""
        addr_type = AddressType(c_addr.type)
        address = [int(n) for n in c_addr.address]
        # qqqdaca mostly guessing, make sure these are correct
        if addr_type is AddressType.IPV4:
            address = address[:4]
        elif addr_type is AddressType.IPV4_PORT:
            address = address[:5]
        elif addr_type is AddressType.IPV6:
            address = address[:8]
        elif addr_type is AddressType.MAC:
            address = address[:6]

        return cls(type=addr_type, address=address)

    def to_c(self):
        """Create a `~canlib.kvrlib.kvrAddress` from this object"""
        c_addr = kvrAddress(self.type)
        c_addr.address[0:len(self.address)] = self.address
        return c_addr

    def __str__(self):
        if self.type is AddressType.IPV4:
            addr = '.'.join(str(x) for x in self.address)
        elif self.type is AddressType.IPV4_PORT:
            addr = '.'.join(str(x) for x in self.address[:-1])
            addr += ':' + str(self.address[-1])
        elif self.type is AddressType.IPV6:
            addr = ':'.join(str(x) for x in self.address)
        elif self.type is AddressType.MAC:
            addr = '-'.join(str(x) for x in self.address)
        else:
            addr = ' '.join(str(x) for x in self.address if x != 0)

        return f'<Address {addr} ({self.type.name})>'
