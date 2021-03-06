import os.path

from canlib import kvlclib

tmp_dir = "tmp"


def setup_infile(datadir, converter):
    inf = os.path.join(datadir, "logfile001.kme50")
    converter.setInputFile(inf, kvlclib.FileFormat.KME50)


def setup_properties(converter):
    converter.setProperty(kvlclib.Property.OVERWRITE, 1)
    converter.setProperty(kvlclib.Property.CHANNEL_MASK, 0x01)


def create_tmp_dir():
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir


def create_outfile_name(name, fmt):
    tmp_dir = create_tmp_dir()
    fname = os.path.join(tmp_dir, name + "." + fmt.extension)
    if os.path.exists(fname):
        print(f"removing {fname}")
        os.remove(fname)
    return fname


def test_version():
    v = kvlclib.dllversion()
    print(v)
    print(v.major, v.minor, v.build)


# creates file plain.txt in dir. src/canlib/tests/tmp
def test_setInputFile_Plain_TXT(datadir):
    fmt = kvlclib.WriterFormat(kvlclib.FileFormat.PLAIN_ASC)
    converter = kvlclib.Converter(create_outfile_name("plain", fmt), fmt)
    assert converter.getProperty(kvlclib.Property.OVERWRITE) == 0
    assert converter.getProperty(kvlclib.Property.CHANNEL_MASK) == 31
    setup_infile(datadir, converter)
    setup_properties(converter)
    assert converter.getProperty(kvlclib.Property.OVERWRITE) == 1
    assert converter.getProperty(kvlclib.Property.CHANNEL_MASK) == 1
    n_new_file_name = 0
    while True:
        try:
            converter.convertEvent()
            if converter.isOutputFilenameNew():
                n_new_file_name += 1
                print(f"New output filename: {converter.getOutputFilename()}")
                print(f"About {converter.eventCount()} events left to convert...")
        except kvlclib.KvlcEndOfFile:
            assert converter.isOverrunActive() == 0
            if converter.isOverrunActive():
                print("NOTE! The extracted data contained overrun.")
                converter.resetOverrunActive()

            assert converter.isDataTruncated() == 0
            if converter.isDataTruncated():
                print("NOTE! The extracted data was truncated.")
                converter.resetStatusTruncated()

            assert converter.isDlcMismatch() == 0
            break

    of = converter.getOutputFilename()
    converter.flush()
    assert n_new_file_name == 1
    assert int(os.path.getsize(of)) > 0


# creates file vector.asc in dir. src/canlib/tests/tmp
def test_setInputFile_Vector_ASC(datadir):
    fmt = kvlclib.WriterFormat(kvlclib.FileFormat.VECTOR_ASC)
    converter = kvlclib.Converter(create_outfile_name("vector", fmt), fmt)
    assert converter.getProperty(kvlclib.Property.OVERWRITE) == 0
    assert converter.getProperty(kvlclib.Property.CHANNEL_MASK) == 31
    setup_infile(datadir, converter)
    setup_properties(converter)
    assert converter.getProperty(kvlclib.Property.OVERWRITE) == 1
    assert converter.getProperty(kvlclib.Property.CHANNEL_MASK) == 1
    n_new_file_name = 0
    while True:
        try:
            converter.convertEvent()
            if converter.isOutputFilenameNew():
                n_new_file_name += 1
                print(f"New output filename: {converter.getOutputFilename()}")
                print(f"About {converter.eventCount()} events left to convert...")
        except kvlclib.KvlcEndOfFile:
            assert converter.isOverrunActive() == 0
            if converter.isOverrunActive():
                print("NOTE! The extracted data contained overrun.")
                converter.resetOverrunActive()

            assert converter.isDataTruncated() == 0
            if converter.isDataTruncated():
                print("NOTE! The extracted data was truncated.")
                converter.resetStatusTruncated()

            assert converter.isDlcMismatch() == 0
            break

    of = converter.getOutputFilename()
    converter.flush()
    assert n_new_file_name == 1
    assert int(os.path.getsize(of)) > 0


def test_reader_formats():
    for fmt in kvlclib.reader_formats():
        print(f'\n{fmt} ({fmt!r})')
        for property in kvlclib.Property:
            if fmt.isPropertySupported(property):
                if kvlclib.properties._PROPERTY_TYPE[property] is None:
                    print(f'\t{property!r} is supported')
                else:
                    print(f'\t{property!r} = {fmt.getPropertyDefault(property)}')
            else:
                print(f'\t{property!r} is not supported')


def test_writer_formats():
    for fmt in kvlclib.writer_formats():
        print(f'\n{fmt} ({fmt!r})')
        for property in kvlclib.Property:
            if fmt.isPropertySupported(property):
                if kvlclib.properties._PROPERTY_TYPE[property] is None:
                    print(f'\t{property!r} is supported')
                else:
                    print(f'\t{property!r} = {fmt.getPropertyDefault(property)}')
            else:
                print(f'\t{property!r} is not supported')
