import pytest

from pathlib import Path
from shutil import copyfile
from canlib import kvlclib

SIGNAL_BASED = kvlclib.Property.SIGNAL_BASED
SIZE_LIMIT = kvlclib.Property.SIZE_LIMIT
TIME_LIMIT = kvlclib.Property.TIME_LIMIT


def cmp_files(f1, f2):
    bufsize = 1
    nbr_missmatches = 0
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            if b1 != b2:
                nbr_missmatches += 1
            if not b1:
                break
    return nbr_missmatches


def convert_events(cnv):
    # Get estimated number of remaining events in the input file. This
    # can be useful for displaying progress during conversion.
    total = cnv.eventCount()
    print("Converting about %d events..." % total)
    while True:
        try:
            # Convert events from input file one by one until EOF
            # is reached
            cnv.convertEvent()
            if cnv.isOutputFilenameNew():
                print(f"New output filename: '{cnv.getOutputFilename()}'")
                print("About %d events left..." % cnv.eventCount())
        except kvlclib.KvlcEndOfFile:
            if cnv.isOverrunActive():
                print("NOTE! The extracted data contained overrun.")
                cnv.resetOverrunActive()
            if cnv.isDataTruncated():
                print("NOTE! The extracted data was truncated.")
                cnv.resetStatusTruncated()
            break


format_prop_support = [
    (kvlclib.FileFormat.CSV, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.CSV_SIGNAL, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: True}),
    (kvlclib.FileFormat.FAMOS, {SIZE_LIMIT: False, TIME_LIMIT: False, SIGNAL_BASED: True}),
    (kvlclib.FileFormat.FAMOS_XCP, {SIZE_LIMIT: False, TIME_LIMIT: False, SIGNAL_BASED: True}),
    (kvlclib.FileFormat.J1587, {SIZE_LIMIT: False, TIME_LIMIT: False, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.KME24, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.KME25, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.KME40, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.KME50, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.KME60, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.MATLAB, {SIZE_LIMIT: False, TIME_LIMIT: True, SIGNAL_BASED: True}),
    (kvlclib.FileFormat.MDF, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.MDF_SIGNAL, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: True}),
    (kvlclib.FileFormat.MDF_4X, {SIZE_LIMIT: False, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.MDF_4X_SIGNAL, {SIZE_LIMIT: False, TIME_LIMIT: True, SIGNAL_BASED: True}),
    (kvlclib.FileFormat.PLAIN_ASC, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.VECTOR_ASC, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.VECTOR_BLF, {SIZE_LIMIT: True, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.VECTOR_BLF_FD, {SIZE_LIMIT: False, TIME_LIMIT: True, SIGNAL_BASED: False}),
    (kvlclib.FileFormat.XCP, {SIZE_LIMIT: False, TIME_LIMIT: False, SIGNAL_BASED: True}),
]

fmt_list = [x[0] for x in format_prop_support]


def setup_converter(datadir, tmp_path, fmt):
    dbc = Path(datadir) / "saab_log_2018-09-06006.dbc"
    kme_file = Path(datadir) / "saab_log_2018-09-06006.kme50"

    in_fmt = kvlclib.ReaderFormat(kvlclib.FileFormat.KME50)
    in_file = tmp_path / kme_file.name
    copyfile(kme_file, in_file)

    try:
        out_fmt = kvlclib.WriterFormat(fmt)
    except kvlclib.KvlcNotImplemented:  # Some writers are not supported on linux
        pytest.skip()

    if out_fmt.isPropertySupported(kvlclib.Property.SIGNAL_BASED):
        dbc_file = tmp_path / dbc.name
        copyfile(dbc, dbc_file)
    else:
        dbc_file = None

    out_file = tmp_path / in_file.name
    suffix = '.' + out_fmt.extension
    out_file = out_file.with_suffix(suffix)

    cnv = kvlclib.Converter(out_file, out_fmt)
    cnv.setInputFile(in_file, in_fmt)
    if dbc_file:
        cnv.addDatabaseFile(dbc_file, channel_mask=0b1111)

    return cnv, out_file, suffix


def split_on_property(datadir, tmp_path, fmt, prop=None, value=None, support=None):
    dbc = Path(datadir) / "saab_log_2018-09-06006.dbc"
    kme = Path(datadir) / "saab_log_2018-09-06006.kme50"

    in_fmt = kvlclib.ReaderFormat(kvlclib.FileFormat.KME50)
    in_file = tmp_path / kme.name
    copyfile(kme, in_file)

    out_fmt = kvlclib.WriterFormat(fmt)
    if out_fmt.isPropertySupported(kvlclib.Property.SIGNAL_BASED):
        dbc_file = tmp_path / dbc.name
        copyfile(dbc, dbc_file)
    else:
        dbc_file = None

    if prop is not None:
        out_file = tmp_path / f"{prop.name}_{in_file.name}"
    else:
        out_file = tmp_path / f"NO_SPLIT_{in_file.name}"
    suffix = '.' + out_fmt.extension
    out_file = out_file.with_suffix(suffix)

    cnv = kvlclib.Converter(out_file, out_fmt)
    cnv.setInputFile(in_file, in_fmt)
    if dbc_file:
        cnv.addDatabaseFile(dbc_file, channel_mask=0b1111)
    if prop is not None:
        try:
            cnv.setProperty(prop, value)
        except kvlclib.KvlcNotImplemented:
            assert support is False, (
                f"{fmt}: {prop.name} is supported by {fmt.name}, "
                f"but setProperty returned NotImplemented"
            )
    convert_events(cnv)
    cnv.flush()  # force flush result to disk


@pytest.mark.parametrize("fmt_prop_supported", format_prop_support, ids=lambda x: f"{x[0].name}")
def test_supported_props(fmt_prop_supported):
    """Verify that support of Size, Time and SIGNAL_BASED is correctly defined"""
    fmt, props = fmt_prop_supported

    try:
        out_fmt = kvlclib.WriterFormat(fmt)
    except kvlclib.KvlcNotImplemented:  # Some writers are not supported on linux
        pytest.skip()

    for prop, is_supported in props.items():
        assert out_fmt.isPropertySupported(prop) == is_supported, (
            f"{fmt.name}: value of 'isPropertySupported({prop.name})' in test is wrong,"
            f" format returns '{out_fmt.isPropertySupported(prop)}'."
        )


@pytest.mark.slow
@pytest.mark.parametrize("fmt_prop_support", format_prop_support, ids=lambda x: x[0].name)
def test_split_in_empty_dir(datadir, tmp_path, fmt_prop_support):
    """Splitting in empty directory using Size, Time, and No limit"""
    fmt, support = fmt_prop_support

    try:
        is_signal_based = kvlclib.WriterFormat(fmt).isPropertySupported(
            kvlclib.Property.SIGNAL_BASED
        )
        has_size_split = kvlclib.WriterFormat(fmt).isPropertySupported(kvlclib.Property.SIZE_LIMIT)
        has_time_split = kvlclib.WriterFormat(fmt).isPropertySupported(kvlclib.Property.TIME_LIMIT)
    except kvlclib.KvlcNotImplemented:  # Some writers are not supported on linux
        pytest.skip()

    print(
        f"{fmt.name}: is_signal_based:{is_signal_based}, has_size_split:{has_size_split},"
        f" has_time_split:{has_time_split}"
    )

    split_on_property(datadir, tmp_path, fmt)
    split_on_property(datadir, tmp_path, fmt, kvlclib.Property.SIZE_LIMIT, 1, has_size_split)
    split_on_property(datadir, tmp_path, fmt, kvlclib.Property.TIME_LIMIT, 60, has_time_split)

    for prop, is_supported in support.items():
        if prop == SIGNAL_BASED:
            break
        size_files = list(tmp_path.glob(f'{prop.name}*'))
        if is_supported:
            assert len(size_files) > 1, (
                f"{fmt.name}: {prop.name} is supported,"
                " but only one file was created (to few data?)."
            )
        else:
            assert len(size_files) == 1, (
                f"{fmt.name}: {prop.name} is not supported, "
                f"but {len(size_files)} files were created."
            )

            nosplit_files = list(tmp_path.glob("NO_SPLIT*"))
            assert (
                len(nosplit_files) == 1
            ), f"{fmt.name}: Converting without split should generate exactly one file."
            nbr_missmatches = cmp_files(size_files[0], nosplit_files[0])
            assert nbr_missmatches == pytest.approx(0, abs=4), (
                f"missmatches: {nbr_missmatches}\n"
                f"{fmt.name}: {prop.name} is not supported, "
                f"but resulting file differ from not setting property by "
                f"{nbr_missmatches} characters ({size_files[0]} differ "
                f"from {nosplit_files[0]})"
            )


@pytest.mark.slow
@pytest.mark.parametrize("part", ["part0", "part1"], ids=lambda x: x)
@pytest.mark.parametrize("fmt", fmt_list, ids=lambda x: x.name)
def test_split_on_size_exists(datadir, tmp_path, fmt, part):
    """Splitting on size in directory where files already exists."""
    cnv, out_file, suffix = setup_converter(datadir, tmp_path, fmt)

    tmp_file = Path(str(out_file).replace(suffix, f"-{part}{suffix}"))
    dummy_text = "Dummy file with same name as expected output"
    tmp_file.write_text(dummy_text)

    is_signal_based = kvlclib.WriterFormat(fmt).isPropertySupported(kvlclib.Property.SIGNAL_BASED)
    has_size_split = kvlclib.WriterFormat(fmt).isPropertySupported(kvlclib.Property.SIZE_LIMIT)
    print(f"{fmt.name}: is_signal_based:{is_signal_based}, has_size_split:{has_size_split}")

    size_split_error_thrown = False
    try:
        cnv.setProperty(kvlclib.Property.SIZE_LIMIT, 1)  # Split size in MB
    except kvlclib.KvlcNotImplemented:
        assert has_size_split is False, (
            f"{fmt}: Split on size is supported by {fmt.name}, "
            f"but setProperty returned NotImplemented"
        )
        size_split_error_thrown = True

    file_exists_error_thrown = False
    try:
        convert_events(cnv)
    except kvlclib.KvlcFileExists:
        file_exists_error_thrown = True
    cnv.flush()  # force flush result to disk

    assert tmp_file.read_text() == dummy_text, f"{fmt.name}: Splitting on size overwrites {part}"

    if size_split_error_thrown:
        no_split_files = len(list(tmp_path.glob("saab_log_2018-09-06006" + suffix)))
        assert (
            no_split_files == 1
        ), f"Split on size signaled NOT_IMPLEMENTED, but {no_split_files} files were created "
    else:
        assert file_exists_error_thrown or size_split_error_thrown, (
            f"{fmt.name}: Writer did not signal FILE_EXISTS"
            f" (but the {part} was not overwritten)."
        )


@pytest.mark.slow
@pytest.mark.parametrize("part", ["part0", "part1"], ids=lambda x: x)
@pytest.mark.parametrize("fmt", fmt_list, ids=lambda x: x.name)
def test_split_on_time_exists(datadir, tmp_path, fmt, part):
    """Splitting on time in directory where a "part" file already exists."""
    cnv, out_file, suffix = setup_converter(datadir, tmp_path, fmt)

    tmp_file = Path(str(out_file).replace(suffix, f"-{part}{suffix}"))
    dummy_text = "Dummy file with same name as expected output"
    tmp_file.write_text(dummy_text)

    is_signal_based = kvlclib.WriterFormat(fmt).isPropertySupported(kvlclib.Property.SIGNAL_BASED)
    has_time_split = kvlclib.WriterFormat(fmt).isPropertySupported(kvlclib.Property.TIME_LIMIT)
    print(f"{fmt.name}: is_signal_based:{is_signal_based}, has_time_split:{has_time_split}")

    time_split_error_thrown = False
    try:
        cnv.setProperty(kvlclib.Property.TIME_LIMIT, 60)  # Delta time in seconds
    except kvlclib.KvlcNotImplemented:
        time_split_error_thrown = True
        assert has_time_split is False, (
            f"{fmt}: Split on time is supported by {fmt.name}, "
            f"but setProperty returned NotImplemented"
        )

    file_exists_error_thrown = False
    try:
        convert_events(cnv)
    except kvlclib.KvlcFileExists:
        file_exists_error_thrown = True
    cnv.flush()  # force flush result to disk

    assert tmp_file.read_text() == dummy_text, f"{fmt.name}: Splitting on time overwrites {part}"

    if time_split_error_thrown:
        no_split_files = len(list(tmp_path.glob("saab_log_2018-09-06006" + suffix)))
        assert (
            no_split_files == 1
        ), f"Split on time signaled NOT_IMPLEMENTED, but {no_split_files} files were created"
    else:
        assert file_exists_error_thrown or time_split_error_thrown, (
            f"{fmt.name}: Writer did not signal FILE_EXISTS"
            f" (but the {part} was not overwritten)."
        )
