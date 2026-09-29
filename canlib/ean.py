from . import deprecation

PRODUCT_EAN_LENGTH = 7


def bcd_digits(bcd_bytes):
    """Split a byte sequence into four-bit BCD digits

    Used internally by `EAN` to decode BCD.

    For example 0x12345 is turned into 1, 2, 3, 4, 5.

    `bcd_bytes` must be an iterable of eight bit objects supporting `&` and
    `>>`.

    Note:
        The byteorder is currently assumed to be 'little'.

    """
    # byteorder is assumed to be 'little'
    for char in bcd_bytes:
        # Python 2 doesn't have bytes, only string
        if isinstance(char, str):
            char = ord(char)
        yield char & 0xF
        yield char >> 4


def int_from_digits(digits, base=10):
    """Joins a sequence of decimal digits into a decimal number

    Used internally by `EAN`.

    For example (1, 2, 3, 4, 5) is turned into 54321.

    Iterating through `digits` is assumed to only yield integers between 0 and
    9, inclusive.

    """
    decimal = 0
    for pos, digit in enumerate(digits):
        decimal += digit * base ** pos
    return decimal


class IllegalEAN(ValueError):
    """Could not parse EAN"""

    pass


class EAN:
    r"""Helper object for dealing with European Article Numbers

    Depending on the format the ean is in, `EAN` objects are created in
    different ways;

    For strings::

        EAN('73-30130-01234-5')

    For integers::

        EAN(7330130012345)

    For iterables of integers::

        EAN([7, 3, 3, 0, 1, 3, 0, 0, 1, 2, 3, 4, 5])

    For BCD-coded bytes or bytearrays (str in python 2)::

        EAN.from_bcd(b'\x45\x23\x01\x30\x01\x33\x07')

    For "hi-lo" format, i.e. two 32-bit integers containing half the ean each,
    both BCD-coded::

        EAN.from_hilo([eanHi, eanLo])

    The various representations can then be produced from the resulting object::

        >>> str(ean)
        '73-30130-01234-5'
        >>> int(ean)
        7330130012345
        >>> tuple(ean)  # or list(), or any other sequence type
        (7, 3, 3, 0, 1, 3, 0, 0, 1, 2, 3, 4, 5)
        >>> ean.bcd()
        b'E#\x010\x013\x07'
        >>> ean.hilo()
        (805380933, 471809)

    Sometimes it is easier to only use the last six digits of the ean, the
    product code and check digit. This is supported when working with string
    representations; the constructor supports six-digit (seven-character) input::

        EAN('01234-5')

    In that cases, the country and manufacturer code is assumed to be that of
    Kvaser AB (73-30130).

    A string containing only the product code and check digit can also be retrieved::

        ean.product()

    Instances can also be indexed which yields specific digits as integers::

        >>> ean[7]
        0
        >>> ean[7:]
        (0, 1, 2, 3, 4, 5)

    Note:
        The byteorder is currently always assumed to be 'little'.

    """
    fmt = "##-#####-#####-#"
    num_digits = len([s for s in fmt if s == '#'])

    @classmethod
    def from_bcd(cls, bcd_bytes):
        """Create an EAN object from a binary coded bytes-like object

        The EAN is automatically shortened to the correct length.

        """
        # The digits are in reverse order, and there is an extra zero
        digits = tuple(bcd_digits(bcd_bytes))[: cls.num_digits]
        digits = reversed(digits)
        return cls(digits)

    @classmethod
    @deprecation.deprecated.favour("the EAN constructor directly")
    def from_string(cls, ean_string):
        """Create an EAN object from a specially formatted string

        .. deprecated:: 1.6
           Use the constructor, `EAN(ean_string)`, instead.

        """
        return cls(ean_string)

    @classmethod
    def from_hilo(cls, hilo):
        """Create an EAN object from a pair of 32-bit integers, (eanHi, eanLo)"""
        high, low = hilo
        # we get three extra digits in 'high'
        high = tuple(bcd_digits(high.to_bytes(4, byteorder='little')))[:-3]
        low = tuple(bcd_digits(low.to_bytes(4, byteorder='little')))
        return cls(high[::-1] + low[::-1])  # and the digits are reversed

    @classmethod
    def _parse_int(cls, ean_int):
        digits_string = str(ean_int).rjust(cls.num_digits, '0')
        internal = tuple(int(d) for d in digits_string)
        if len(internal) != cls.num_digits:
            raise IllegalEAN("Too large EAN integer: " + str(ean_int))
        else:
            return internal

    @classmethod
    def _parse_str(cls, ean_string):
        if len(ean_string) == PRODUCT_EAN_LENGTH:
            ean_string = "73-30130-" + ean_string

        if len(ean_string) != len(cls.fmt):
            raise IllegalEAN("Wrong length for EAN string: " + repr(ean_string))
        if not all(s.isdigit() if (f == '#') else (f == s) for f, s in zip(cls.fmt, ean_string)):
            raise IllegalEAN("Unreconized format for EAN string: " + repr(ean_string))

        internal = tuple(int(s) for f, s in zip(cls.fmt, ean_string) if f == '#')
        return internal

    def __init__(self, source):
        if isinstance(source, str):
            self._internal = self._parse_str(source)
        elif isinstance(source, int):
            self._internal = self._parse_int(source)
        else:
            # Assumed to be a iterable
            internal = tuple(source)
            if len(internal) != self.num_digits:
                raise IllegalEAN(f"Wrong length of EAN sequence ({len(internal)})")
            elif not all(isinstance(d, int) for d in internal):
                raise IllegalEAN("EAN sequence must contain only ints")
            else:
                self._internal = internal

    # required in Python 2
    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        if isinstance(other, EAN):
            return self._internal == other._internal
        elif isinstance(other, str):
            return str(self) == other
        else:
            return NotImplemented

    def __getitem__(self, index):
        return self._internal[index]

    def __int__(self):
        return int_from_digits(reversed(self._internal))

    def __iter__(self):
        return iter(self._internal)

    def __str__(self):
        num_only = map(str, self._internal)
        out = ''.join(next(num_only) if s == '#' else s for s in self.fmt)
        if __debug__:
            # check that all digits where printed
            rest = tuple(num_only)
            assert len(rest) == 0, rest
        return out

    def __repr__(self):
        return f"{self.__class__.__name__}('{str(self)}')"

    def __hash__(self):
        return hash(str(self))

    def bcd(self):
        """Return a binary-coded bytes object with this EAN"""
        digits_string = ''.join(str(d) for d in self._internal)
        # fromhex requires an even number of digits
        bcd = bytes.fromhex('0' + digits_string)
        bcd = bytes(reversed(bcd))
        return bcd

    def hilo(self):
        """Return a pair of 32-bit integers, (eanHi, eanLo), with this EAN"""
        high = self._internal[:-8]
        low = self._internal[-8:]
        high = int_from_digits(reversed(high), base=16)
        low = int_from_digits(reversed(low), base=16)
        return (high, low)

    def product(self):
        """Return only the product code and check digit of the string representation"""
        return str(self)[-PRODUCT_EAN_LENGTH:]
