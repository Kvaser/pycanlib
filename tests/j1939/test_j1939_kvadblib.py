import pathlib
import pytest

import source_frames_v5_1 as source_frames

from canlib import j1939
from canlib import kvadblib
from canlib import canlib

DBC_FILE_NEW_FORMAT = pathlib.Path(__file__).parent.absolute() / "j1939_new_format_sample.dbc"
DBC_FILE_OLD_FORMAT = pathlib.Path(__file__).parent.absolute() / "j1939_old_format_sample.dbc"


def info_id(pdu_frame):
    return pdu_frame[0][0]


@pytest.mark.parametrize("info_frame", source_frames.all_frames, ids=info_id)
def test_j1939_new_dbc(info_frame):
    with kvadblib.Dbc(str(DBC_FILE_NEW_FORMAT)) as dbc:
        info, frame = info_frame
        expected_name = info[0].rsplit(' ')[0]  # First word in first metadata is msg name
        pdu = j1939.pdu_from_can_id(frame.id)
        print(f"\nExamining: {frame}")
        print(f"\t{info}")
        # Lookup pdu in DBC using kvadblib
        pgn = pdu.pgn
        print(f"\tLooking for msg with pgn=0x{pgn:x} in dbc")
        # Some CAN frames (non-j1939 frames) will be found in dbc since the
        # calculated pgn matches an existing pgn.
        # Here we define the messages that will be shadowed, e.g. interpreting
        # the CAN id of CANEXT1 as a j1939 frame will end up with a match in
        # the dbc file for JLCM.
        shadows = {
            0x9900: "JLCM",  # CANEXT1
            0xfe4b: "TCFG2",  # CANEXT2
            0: "TSC1",  # CANEXT3
        }
        if pgn in shadows:
            if expected_name != {shadows[pgn]}:
                print(f"\tChanging expected name from {expected_name} to {shadows[pgn]}")
                expected_name = shadows[pgn]
        can_id = frame.id
        # when calling get_message_by_pgn, the EXT flag must be attached to the CAN ID
        if canlib.MessageFlag.EXT in frame.flags:
            can_id |= kvadblib.MessageFlag.EXT
        if info[1]:
            # We expect a hit in the dbc file
            msg = dbc.get_message_by_pgn(can_id)
            assert msg.name == expected_name
        else:
            # We did not expect any hit in the dbc file
            with pytest.raises(kvadblib.KvdNoMessage):
                dbc.get_message_by_pgn(can_id)


@pytest.mark.parametrize("info_frame", source_frames.all_frames, ids=info_id)
def test_j1939_old_dbc(info_frame):
    with kvadblib.Dbc(str(DBC_FILE_OLD_FORMAT)) as dbc:
        # frame will be the frame sent on the bus, info will hold meta data
        info, frame = info_frame
        expected_name = info[0].rsplit(' ')[0]  # First word in first metadata is msg name
        pdu = j1939.pdu_from_can_id(frame.id)
        print(f"\nExamining: id:0x{frame.id:x}, {frame}")
        print(f"\t{info}")
        # lookup pdu in DBC using kvadblib
        pgn = pdu.pgn
        print(f"\tLooking for msg with pgn=0x{pgn:x} in dbc")
        # Some CAN frames will be found in dbc since the calculated pgn is correct:
        shadows = {
            0x9900: "JLCM",  # CANEXT1
            0xfe4b: "TCFG2",  # CANEXT2
            0: "TSC1",  # CANEXT3
        }
        if pgn in shadows:
            if expected_name != {shadows[pgn]}:
                print(f"\tChanging expected name from {expected_name} to {shadows[pgn]}")
                expected_name = shadows[pgn]
        can_id = frame.id
        # when calling get_message_by_pgn, any EXT flag on the frame must be
        # attached to the CAN ID
        if canlib.MessageFlag.EXT in frame.flags:
            can_id |= kvadblib.MessageFlag.EXT
        if info[2]:
            # We expect a hit in the dbc file
            msg = dbc.get_message_by_pgn(can_id)
            assert msg is not None
            assert msg.name == expected_name
        else:
            # We did not expecpt any hit in the dbc file
            with pytest.raises(kvadblib.KvdNoMessage):
                dbc.get_message_by_pgn(can_id)



# If we call get_message_by_id, we still get J1939 messages, which the user
# need to filter out using ID-Format (J1939 PG)


@pytest.mark.parametrize("info_frame", source_frames.can_frames, ids=info_id)
def test_can_new_dbc(info_frame):
    with kvadblib.Dbc(str(DBC_FILE_NEW_FORMAT)) as dbc:
        info, frame = info_frame
        # Lookup message based on CAN id.
        print(f"\nExamining: id:{hex(frame.id)} {frame}")
        print(f"\t{info}")
        can_id = frame.id
        flags = 0
        if canlib.MessageFlag.EXT in frame.flags:
            flags = kvadblib.MessageFlag.EXT
        msg = dbc.get_message_by_id(can_id, flags)
        print(f"Found {msg.name} in new dbc")
        assert msg.name == info[0].rsplit(' ')[0]  # First word is msg name


@pytest.mark.parametrize("info_frame", source_frames.can_frames, ids=info_id)
def test_can_old_dbc(info_frame):
    with kvadblib.Dbc(str(DBC_FILE_OLD_FORMAT)) as dbc:
        info, frame = info_frame
        expected_name = info[0].rsplit(' ')[0]  # First word in first metadata is msg name
        # Lookup message based on CAN id.
        print(f"\nExamining: id:{hex(frame.id)} {frame}")
        print(f"\t{info}")
        can_id = frame.id
        flags = 0
        # The following CAN messages will get a hit in the old format dbc
        shadows = {
            'CANEXT1': None,
            'CANEXT2': None,
            'CANEXT3': 'TC1',  # can_id: 0x100
            'CANEXT4': 'TCFG2',  # can_id: 0xFE4B
        }
        if expected_name in shadows:
            expected_name = shadows[expected_name]

        if canlib.MessageFlag.EXT in frame.flags:
            flags = kvadblib.MessageFlag.EXT
        if expected_name is not None:
            msg = dbc.get_message_by_id(can_id, flags)
            print(f"Found {msg.name} in old dbc")
            assert msg.name == expected_name
        else:
            with pytest.raises(kvadblib.KvdNoMessage):
                dbc.get_message_by_id(can_id, flags)
