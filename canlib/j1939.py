"""

This module holds definitions of J1939 Protocol Data Unit (PDU) frames.

Example of usage:

    >>> from canlib import Frame, j1939
    >>> from canlib.canlib import MessageFlag
    >>> def frame_from_pdu(pdu):
    ...     can_id = j1939.can_id_from_pdu(pdu)
    ...     frame = Frame(
    ...         id_=can_id,
    ...         data=pdu.data,
    ...         flags=MessageFlag.EXT,
    ...     )
    ...     return frame
    >>> pdu = j1939.Pdu1(
    ...     p=3, edp=0, dp=0, pf=0x99, ps=0xfe, sa=0xfe,
    ...     data=[1]
    ... )
    >>> frame_from_pdu(pdu)
    Frame(id=211418878, data=bytearray(b'\\x01'), dlc=1, flags=<MessageFlag.EXT: 4>, timestamp=None)


The particular characteristics of J1939 are:

 - Extended CAN identifier (29 bit)
 - Bit rate 250 kbit/s
 - Peer-to-peer and broadcast communication
 - Transport protocols for up to 1785 data bytes
 - Network management
 - Definition of parameter groups for commercial vehicles and others
 - Manufacturer specific parameter groups are supported
 - Diagnostics features


(Extended) Data Page Bit
************************

+-----------+-----------+----------------------------------------------+
| Extended  |           |                                              |
| Data page | Data page | Description                                  |
+===========+===========+==============================================+
|         0 |         0 | SAE J1939 Page 0 Parameter Groups            |
+-----------+-----------+----------------------------------------------+
|         0 |         1 | SAE J1939 Page 1 Parameter Groups (NMEA2000) |
+-----------+-----------+----------------------------------------------+
|         1 |         1 | SAE J1939 reserved                           |
+-----------+-----------+----------------------------------------------+
|         1 |         1 | ISO 15765-3 defined                          |
+-----------+-----------+----------------------------------------------+

    .. versionadded:: 1.18

"""
# Reference:
# https://assets.vector.com/cms/content/know-how/_application-notes/AN-ION-1-3100_Introduction_to_J1939.pdf
# https://forums.ni.com/t5/Example-Code/J1939-Transport-Protocol-Reference-Example/ta-p/3984291?profile.language=en

from pydantic import BaseModel
from typing import Optional, Any, List


class Pdu(BaseModel):
    """Protocol Data Unit in j1939.

    Base class with attributes common to `Pdu1` and `Pdu2`

    """
    p: int  #: priority
    edp: int  #: extended data page
    dp: int  #: data page
    pf: int  #: PDU format
    ps: int  #: PDU specific
    sa: int  #: source address
    data: Optional[List[int]] = None #: data field

    def __repr__(self):
        return (f"p={self.p}, edp={self.edp}, dp={self.dp},"
                f" pf=0x{self.pf:02x}, ps=0x{self.ps:02x},"
                f" sa=0x{self.sa:02x}, data={self.data})")


class Pdu1(Pdu):
    """Protocol Data Unit, Format 1

    When `Pdu.pf` < 240, the PDU Specific field is a Destination Address and

    `pgn` = Extended Data Page + Data Page + PDU Format + "00"

    """
    da: Optional[int] = None #: destination address, `Pdu.ps`
    pgn: Optional[int] = None  #: parameter group number

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.da = self.ps
        self.pgn = self.pf << 8

    def __str__(self):
        return (f"pgn=0x{self.pgn:x}: Pdu1({super().__repr__()}")


class Pdu2(Pdu):
    """Protocol Data Unit, Format 2

    When `Pdu.pf` >= 240, the PDU Specific field is the Group Extension

      `pgn` = Extended Data Page + Data Page + PDU Format + Group Extension

    """
    ge: Optional[int] = None #: group extension, equal to `Pdu.ps`
    pgn: Optional[int] = None #: parameter group number

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.ge = self.ps
        self.pgn = (self.pf << 8) + self.ps

    def __str__(self):
        return (f"pgn=0x{self.pgn:x}: Pdu2({super().__repr__()}")


def pdu_from_can_id(can_id):
    """Create j1939 Protocol Data Unit object based on CAN Id.

    Args:
        can_id (`int`): CAN Identifier

    Returns:
        `Pdu1` or `Pdu2` depending on value of `can_id`

    """
    sa = can_id & (0xff)
    ps = (can_id & (0xff << 8)) >> 8
    pf = (can_id & (0xff << 16)) >> 16
    p = (can_id & (0b111 << 26)) >> 26
    edp = (can_id & (0b1 << 25)) >> 25
    dp = (can_id & (0b1 << 24)) >> 24
    if pf < 239:
        # pgn = pf
        return Pdu1(p=p, edp=edp, dp=dp, pf=pf, ps=ps, sa=sa)
    else:
        # pgn = (pf << 8) + ps
        return Pdu2(p=p, edp=edp, dp=dp, pf=pf, ps=ps, sa=sa)


def can_id_from_pdu(pdu):
    """Extract CAN Id based on j1939 Protocol Data Unit object.

    Args:
        pdu (`Pdu1` or `Pdu2`): Protocol Data Unit

    Returns:
        can_id (`int`): CAN Identifier

    """
    # can_id =  0x80000000  # Extended flag in id
    can_id = pdu.sa
    can_id |= pdu.ps << 8
    can_id |= pdu.pf << 16
    can_id |= pdu.p << 26
    can_id |= pdu.dp << 24
    can_id |= pdu.edp << 25
    return can_id
