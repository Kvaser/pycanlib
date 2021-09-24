import pandas as pd
import pathlib
import pytest

import source_frames_v5_1 as source_frames

from canlib import kvlclib

DBC_FILE_NEW_FORMAT = pathlib.Path(__file__).parent.absolute() / "j1939_new_format_sample.dbc"
DBC_FILE_OLD_FORMAT = pathlib.Path(__file__).parent.absolute() / "j1939_old_format_sample.dbc"
KME50_FILE = pathlib.Path(__file__).parent.absolute() / "j1939_test_v5_1.kme50"


@pytest.mark.parametrize(
    "dbcfile, expected_signals, outname",
    [
        pytest.param(DBC_FILE_NEW_FORMAT, source_frames.new_dbc_expected_signals, "myresult_new_signal", id="newformat"),
        pytest.param(DBC_FILE_OLD_FORMAT, source_frames.old_dbc_expected_signals, "myresult_old_signal", id="oldformat"),
    ]
)
def test_j1939_dbc_to_signal_csv(dbcfile, expected_signals, outname):
    # set up formats
    out_fmt = kvlclib.WriterFormat(kvlclib.FileFormat.CSV_SIGNAL)
    in_fmt = kvlclib.ReaderFormat(kvlclib.FileFormat.KME50)

    # set resulting output file name taking advantage of the extension
    # defined in the format.
    out_file = f"{outname}." + out_fmt.extension
    print(f"Output filename is '{out_file}'")

    # create converter
    cnv = kvlclib.Converter(out_file, out_fmt)

    # Set input file and format
    cnv.setInputFile(KME50_FILE, in_fmt)
    print(f"Input filename is '{KME50_FILE}'")

    # Add database
    cnv.addDatabaseFile(str(dbcfile), channel_mask=1)
    print(f"Using database '{dbcfile}'")

    # we are interpreting incoming frames as j1939
    cnv.setProperty(kvlclib.Property.HLP_J1939, 1)

    # we are only interested in the first channel
    cnv.setProperty(kvlclib.Property.CHANNEL_MASK, 1)

    # allow output file to overwrite existing files
    cnv.setProperty(kvlclib.Property.OVERWRITE, 1)

    # add nice header to the output file
    cnv.setProperty(kvlclib.Property.WRITE_HEADER, 1)

    # Convert events from input file one by one until EOF is reached
    while True:
        try:
            cnv.convertEvent()
        except kvlclib.KvlcEndOfFile:
            break

    # Force a flush so that the resulting file is written to disk.
    cnv.flush()

    # Create array of dictionary for all signals
    rows = []
    df = pd.read_csv(out_file, skiprows=6)
    for i in range(len(df)):
        row = df.iloc[i].dropna()
        rows.append(row.to_dict())

    # Manual specification of time offset between source_frames.py and kme50 file
    time_offset = 1.1557
    # Compare all items
    for i, item in enumerate(expected_signals):
        print(
            f"Looking at index {i}, timestamp {rows[i]['Timestamp']} vs "
            f"{expected_signals[i]['Timestamp']}"
        )
        rows[i]['Timestamp'] = round(rows[i]['Timestamp'] - time_offset)
        # qqqmac ignore wrong dlc for now (dlc mismatch is currently not ignored by kvlclib) BLA-2606
        if len(item) > 1:
            assert rows[i] == expected_signals[i]
        else:
            print(f"\tignoring {i} since dlc differ ()...")
