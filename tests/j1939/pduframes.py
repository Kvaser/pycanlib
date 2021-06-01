"""This module specifies test data for the j1939 tests

See Readme.txt for more information.

"""

import random

from canlib import canlib, Frame, j1939


def some_data(length):
    data = [random.randint(0, 255) for x in range(length)]
    return data


def frame_from_pdu(pdu):
    can_id = j1939.can_id_from_pdu(pdu)
    frame = Frame(
        id_=can_id,
        data=pdu.data,
        flags=canlib.MessageFlag.EXT,
    )
    return frame


def info_id(pdu_frame):
    return pdu_frame[0][0]


# Format of info tuple:
# "name", pass using new format dbc, pass using old format dbc, "reason"
pdu1_frames = [
    (
        ("JLCM pgn=0x9900", True, True, "pgn exists in dbc"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=0, pf=0x99, ps=0xfe, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        ("JLCM (sa=0x02)", True, True, "sa not part of pgn"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=0, pf=0x99, ps=0xfe, sa=0x02, data=some_data(length=8))
        ),
    ),
    (
        ("TC1 pgn=0x100", True, True, "pgn exists in dbc"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=0, pf=0x01, ps=0xfe, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        ("TSC1 pgn=0", True, True, "pgn exists in dbc"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=0, pf=0x00, ps=0xfe, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        ("TSC1 (sa=0xff)", True, True, "sa not part of pgn"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=0, pf=0x00, ps=0xfe, sa=0xff, data=some_data(length=8))
        ),
    ),
    (
        ("TSC1 (sa=0)", True, True, "sa not part of pgn"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=0, pf=0x00, ps=0xfe, sa=0x00, data=some_data(length=8))
        ),
    ),
    (
        ("JLCM (p)", True, True, "p is not part of pgn"),
        frame_from_pdu(
            j1939.Pdu1(p=2, edp=0, dp=0, pf=0x99, ps=0xfe, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        ("JLCM (ps)", True, True, "ps is not part of pgn for pdu2"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=0, pf=0x99, ps=0xf0, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        ("Divider", False, False, "not in dbc"),
        Frame(id_=333, flags=canlib.MessageFlag.STD, data=bytearray(b'-----')),
    ),
    (
        ("TSC1 (p)", True, True, "p is not part of pgn"),
        frame_from_pdu(
            j1939.Pdu1(p=2, edp=0, dp=0, pf=0x00, ps=0xfe, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        # kvlclib currently returns signals with random (uninitialized) data when dlc does not match. BLA-2606
        ("DM19 pgn=0xD300", True, True, "DM19 dlc > frame dlc"),
        frame_from_pdu(
            j1939.Pdu1(p=6, edp=0, dp=0, pf=0xd3, ps=0xfe, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        # kvlclib currently returns signals with random (uninitialized) data when dlc does not match. BLA-2606
        ("DM19 (sa=0xfa)", True, True, "DM19 dlc > frame dlc"),
        frame_from_pdu(
            j1939.Pdu1(p=6, edp=0, dp=0, pf=0xd3, ps=0xfe, sa=0xfa, data=some_data(length=8))
        ),
    ),
    (
        # kvlclib currently returns signals with random (uninitialized) data when dlc does not match. BLA-2606
        ("JLCM wrong DLC", True, True, "JLCM dlc > frame dlc"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=0, pf=0x99, ps=0xfe, sa=0xfe, data=some_data(length=4))
        ),
    ),
    (
        ("JLCM (edp)", False, False, "edp is part of pgn"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=1, dp=0, pf=0x99, ps=0xfe, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        ("JLCM (dp)", False, False, "dp is part of pgn"),
        frame_from_pdu(
            j1939.Pdu1(p=3, edp=0, dp=1, pf=0x99, ps=0xfe, sa=0xfe, data=some_data(length=8))
        ),
    ),
]

pdu2_frames = [
    (
        ("TCFG2 (p)", True, True, "p is not part of pgn"),
        frame_from_pdu(
            j1939.Pdu2(p=4, edp=0, dp=0, pf=0xfe, ps=0x4b, sa=0xfe, data=some_data(length=2))
        ),
    ),
    (
        ("TCFG2 pgn=0xFE4B", True, True, "pgn exists in dbc"),
        frame_from_pdu(
            j1939.Pdu2(p=6, edp=0, dp=0, pf=0xfe, ps=0x4b, sa=0xfe, data=some_data(length=2))
        ),
    ),
    (
        ("Divider", False, False, "not in dbc"),
        Frame(id_=333, flags=canlib.MessageFlag.STD, data=bytearray(b'-----')),
    ),
    (
        # kvlclib currently returns signals with random (uninitialized) data when dlc does not match. BLA-2606
        # Right now we create an expecteded message with now signals, {'Timestamp': 11} in new_dbc_expected_signals and new_dbc_expected_signals
        ("EC1 pgn=0xFEE3", True, True, "EC1 dlc > frame dlc"),
        frame_from_pdu(
            j1939.Pdu2(p=6, edp=0, dp=0, pf=0xfe, ps=0xe3, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        # kvlclib currently returns signals with random (uninitialized) data when dlc does not match. BLA-2606
        # Right now we create an expecteded message with now signals, {'Timestamp': 11} in new_dbc_expected_signals and new_dbc_expected_signals
        ("EC1 (sa=0)", True, True, "EC1 dlc > frame dlc"),
        frame_from_pdu(
            j1939.Pdu2(p=6, edp=0, dp=0, pf=0xfe, ps=0xe3, sa=0x00, data=some_data(length=8))
        ),
    ),
    (
        # kvlclib currently returns signals with random (uninitialized) data when dlc does not match. BLA-2606
        # Right now we create an expecteded message with now signals, {'Timestamp': 11} in new_dbc_expected_signals and new_dbc_expected_signals
        ("EC1 (sa=0x10)", True, True, "EC1 dlc > frame dlc"),
        frame_from_pdu(
            j1939.Pdu2(p=6, edp=0, dp=0, pf=0xfe, ps=0xe3, sa=0x10, data=some_data(length=8))
        ),
    ),
    (
        # kvlclib currently returns signals with random (uninitialized) data when dlc does not match. BLA-2606
        # Right now we create an expecteded message with now signals, {'Timestamp': 11} in new_dbc_expected_signals and new_dbc_expected_signals
        ("TCFG2 wrong DLC", True, True, "TCFG2 dlc < frame dlc"),
        frame_from_pdu(
            j1939.Pdu2(p=6, edp=0, dp=0, pf=0xfe, ps=0x4b, sa=0xfe, data=some_data(length=8))
        ),
    ),
    (
        ("TCFG2 (edp)", False, False, "edp is part of pgn"),
        frame_from_pdu(
            j1939.Pdu2(p=6, edp=1, dp=0, pf=0xfe, ps=0x4b, sa=0xfe, data=some_data(length=2))
        ),
    ),
    (
        ("TCFG2 (dp)", False, False, "dp is part of pgn"),
        frame_from_pdu(
            j1939.Pdu2(p=6, edp=0, dp=1, pf=0xfe, ps=0x4b, sa=0xfe, data=some_data(length=2))
        ),
    ),
    (
        ("TCFG2 (ps)", False, False, "ps is part of pgn for pdu2"),
        frame_from_pdu(
            j1939.Pdu2(p=6, edp=0, dp=0, pf=0xfe, ps=0x4c, sa=0xfe, data=some_data(length=2))
        ),
    ),
]

wrong = [
    (
        ("TC1 (std flag)", False, False, "pgn need EXT flag"),
        Frame(id_=0x100, data=some_data(length=8), flags=canlib.MessageFlag.STD),
    ),
    (
        ("??? (std flag)", False, False, "pgn need EXT flag"),
        Frame(id_=0x6FE, data=some_data(length=8), flags=canlib.MessageFlag.STD),
    ),
    (
        ("TSC1 (std flag)", False, False, "pgn need EXT flag"),
        Frame(id_=0x0, data=some_data(length=8), flags=canlib.MessageFlag.STD),
    ),
    (
        # kvadblib interpret this as pgn 0 when EXT flag is set
        ("TSC1 <<??? Could be confused with pgn 0x100", True, True, "pgn not in dbc"),
        Frame(id_=100, data=some_data(length=8), flags=canlib.MessageFlag.EXT),
    ),
    (
        # kvadblib interpret this as pgn 0 when EXT flag is set
        ("TSC1 <<??? VECTOR__INDEPENDENT_SIG_MSG, ID=0x40000000", True, True, "not part of dbc"),
        Frame(id_=0, data=[], dlc=0, flags=canlib.MessageFlag.EXT),
    ),
]

can_frames = [
    (
        ("CANSTD1", False, False, "CAN std frame"),  # Old dbc does not look at ID-Format
        Frame(id_=0x100, data=some_data(length=8), flags=canlib.MessageFlag.STD),
    ),
    (
        ("CANSTD2", False, False, "CAN std, no signals"),
        Frame(id_=0x101, data=some_data(length=8), flags=canlib.MessageFlag.STD),
    ),
    (
        # Old dbc format can not distingish from pgn 0x100
        ("CANEXT1", True, True, "CAN ext frame"),
        Frame(id_=0x499FEFE, data=some_data(length=8), flags=canlib.MessageFlag.EXT),
    ),
    (
        ("CANEXT2", True, True, "CAN ext frame"),  # qqqmac new dbc: confused with TCFG2 by EXT flag -> No getMsgByPGN assumes pgn
        Frame(id_=0x8FE4BFE, data=some_data(length=2), flags=canlib.MessageFlag.EXT),
    ),
    (
        # Old db cannot differentiate CAN ext from J1939 PG
        ("CANEXT3", True, True, "CAN ext frame"),  # qqqmac new dbc: confused with pgn 0 by EXT flag
        Frame(id_=0x100, data=some_data(length=8), flags=canlib.MessageFlag.EXT),
    ),
    (
        # Old db cannot differentiate CAN ext from J1939 PG
        ("CANEXT4", True, True, "CAN ext frame"),  # qqqmac new dbc: confused with pgn 0 by EXT flag
        Frame(id_=0xFE4B, data=some_data(length=2), flags=canlib.MessageFlag.EXT),
    ),
]

divider = [
    (
        ("Divider", False, False, "not in dbc"),
        Frame(id_=222, flags=canlib.MessageFlag.STD, data=bytearray(b'=====')),
    )
]

frames = (
    divider +
    pdu1_frames +
    divider +
    pdu2_frames +
    divider +
    wrong +
    divider +
    can_frames +
    divider
)
