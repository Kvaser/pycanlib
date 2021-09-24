"""Send CAN frames for recording and generate expected values in DATA_FILE

See Readme.txt for more info

"""

import datetime
import pathlib
import random
import time

import j1939
from canlib import Device, EAN, Frame, canlib, kvadblib

import pduframes

GENERATOR_DEVICE = Device(ean=EAN("00752-9"), serial=1014)

DBC_FILE_NEW_FORMAT = pathlib.Path(__file__).parent.absolute() / "j1939_new_format_sample.dbc"
DBC_FILE_OLD_FORMAT = pathlib.Path(__file__).parent.absolute() / "j1939_old_format_sample.dbc"

DATA_FILE = pathlib.Path(__file__).parent.absolute() / "source_frames_v5_1.py"


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


def extract_signals_phys(db, frame):
    try:
        bmsg = db.interpret(frame, j1939)
    except kvadblib.KvdNoMessage:
        print(f"\t<<< No message found for frame with id {frame.id} (0x{frame.id:x}) >>>")
        return {}

    if (bmsg._message.dlc != bmsg._frame.dlc):
        print(f"\t<<< Could not interpret message because DLC does not match for frame with id {frame.id} >>>")
        print(f"\t\t- DLC (database): {bmsg._message.dlc} vs DLC (received frame): {bmsg._frame.dlc}")
        return {}

    signals = {}
    for bsig in bmsg:
        signals[bsig.name] = bsig.phys
    return signals


if __name__ == "__main__":
    dev = GENERATOR_DEVICE
    source_frames = []
    can_frames = []
    new_dbc_expected_signals = []
    old_dbc_expected_signals = []
    new_db = kvadblib.Dbc(filename=str(DBC_FILE_NEW_FORMAT))
    old_db = kvadblib.Dbc(filename=str(DBC_FILE_OLD_FORMAT))

    with dev.open_channel(0, bitrate=canlib.Bitrate.BITRATE_250K) as ch_0:
        with dev.open_channel(1, bitrate=canlib.Bitrate.BITRATE_250K) as ch_1:
            ch_0.busOn()
            ch_1.busOn()
            now = time.time()
            for info, frame in pduframes.frames:
                t = time.time() - now
                frame.timestamp = int(t)
                print(f"Write: ({t:.0f}s), Frame(id_=0x{frame.id:x}, "
                      f"dlc={frame.dlc}, data=0x{frame.data.hex()}, "
                      f"flags={frame.flags!r}), {info}")
                row = (
                    f"    ({info}, "
                    f"Frame(id_=0x{frame.id:x}, dlc={frame.dlc}, "
                    f"data={frame.data}, flags=MessageFlag({frame.flags}), "
                    f"timestamp={frame.timestamp}))"
                )
                msg_name = info[0].rsplit(' ')[0]  # First word is msg name
                source_frames.append(row)
                if msg_name.startswith("CAN"):
                    can_frames.append(row)
                if info[1]:
                    # We expect a hit in the new format dbc_file
                    expected_signal = extract_signals_phys(new_db, frame)
                    expected_signal['Timestamp'] = int(t)
                    new_dbc_expected_signals.append(expected_signal)
                if info[2]:
                    # We expect a hit in the old format dbc_file
                    expected_signal = extract_signals_phys(old_db, frame)
                    expected_signal['Timestamp'] = int(t)
                    old_dbc_expected_signals.append(expected_signal)
                ch_0.write(frame)
                msg = ch_1.read(timeout=1000)
                if msg != frame:
                    print(f"Read: {msg.id:x}, {msg}")
                    assert msg == frame
                time.sleep(1)

    # Create DATA_FILE and write data sent and expected values
    with pathlib.Path(DATA_FILE).open(mode='w') as data_file:
        data_file.write(
            "# This file was automatically created by create_log_file.py"
            "# It holds information about contents of j1939_test_v5_1.kme50"
            "# and expected results for use in j1939 kvlclib tests."
            f"# File created {str(datetime.datetime.now())}\n"
            "from canlib import Frame\n"
            "from canlib.canlib import MessageFlag\n"
        )
        data_file.write("all_frames = [\n")
        for item in source_frames:
            data_file.write(f"{item},\n")
        data_file.write("]\ncan_frames = [\n")
        for item in can_frames:
            data_file.write(f"{item},\n")
        data_file.write("]\n")
        data_file.write("new_dbc_expected_signals = [\n")
        for item in new_dbc_expected_signals:
            data_file.write(f"{item},\n")
        data_file.write("]\n")
        data_file.write("old_dbc_expected_signals = [\n")
        for item in old_dbc_expected_signals:
            data_file.write(f"{item},\n")
        data_file.write("]\n")
