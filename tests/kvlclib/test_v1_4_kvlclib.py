import os.path

from conftest import kvdeprecated

from canlib import kvlclib

tmp_dir = "tmp"


def setup_infile(datadir, kvlc):
    inf = os.path.join(datadir, "logfile001.kme50")
    kvlc.setInputFile(inf, kvlclib.FILE_FORMAT_KME50)


def setup_properties(kvlc):
    kvlc.setProperty(kvlclib.PROPERTY_OVERWRITE, 1)
    kvlc.setProperty(kvlclib.PROPERTY_CHANNEL_MASK, 0x01)


def create_tmp_dir():
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir


def create_outfile_name(name, fmt):
    tmp_dir = create_tmp_dir()
    fname = os.path.join(tmp_dir, name + "." + fmt.extension)
    if os.path.exists(fname):
        print("removing %s" % fname)
        os.remove(fname)
    return fname


@kvdeprecated
def test_import_kvlclib():
    fmt = kvlclib.WriterFormat(kvlclib.FILE_FORMAT_PLAIN_ASC)
    kvlc = kvlclib.Kvlclib(create_outfile_name("apa", fmt), fmt)
    print("Python kvlclib version: v%s" % kvlc.getVersion())
    kvlc.deleteConverter()


# creates file plain.txt in dir. src/canlib/tests/tmp
@kvdeprecated
def test_setInputFile_Plain_TXT(datadir):
    fmt = kvlclib.WriterFormat(kvlclib.FILE_FORMAT_PLAIN_ASC)
    kvlc = kvlclib.Kvlclib(create_outfile_name("plain", fmt), fmt)
    assert kvlc.getProperty(kvlclib.PROPERTY_OVERWRITE) == 0
    assert kvlc.getProperty(kvlclib.PROPERTY_CHANNEL_MASK) == 31
    setup_infile(datadir, kvlc)
    setup_properties(kvlc)
    assert kvlc.getProperty(kvlclib.PROPERTY_OVERWRITE) == 1
    assert kvlc.getProperty(kvlclib.PROPERTY_CHANNEL_MASK) == 1
    n_new_file_name = 0
    while True:
        try:
            kvlc.convertEvent()
            if kvlc.IsOutputFilenameNew():
                n_new_file_name += 1
                print("New output filename: %s" % kvlc.getOutputFilename())
                print("About %d events left to convert..." % kvlc.eventCount())
        except kvlclib.KvlcEndOfFile:
            assert kvlc.IsOverrunActive() == 0
            if kvlc.IsOverrunActive():
                print("NOTE! The extracted data contained overrun.")
                kvlc.resetOverrunActive()

            assert kvlc.IsDataTruncated() == 0
            if kvlc.IsDataTruncated():
                print("NOTE! The extracted data was truncated.")
                kvlc.resetStatusTruncated()
            break

    of = kvlc.getOutputFilename()
    kvlc.deleteConverter()
    assert n_new_file_name == 1
    assert int(os.path.getsize(of)) > 0


# creates file vector.asc in dir. src/canlib/tests/tmp
@kvdeprecated
def test_setInputFile_Vector_ASC(datadir):
    fmt = kvlclib.WriterFormat(kvlclib.FILE_FORMAT_VECTOR_ASC)
    kvlc = kvlclib.Kvlclib(create_outfile_name("vector", fmt), fmt)
    assert kvlc.getProperty(kvlclib.PROPERTY_OVERWRITE) == 0
    assert kvlc.getProperty(kvlclib.PROPERTY_CHANNEL_MASK) == 31
    setup_infile(datadir, kvlc)
    setup_properties(kvlc)
    assert kvlc.getProperty(kvlclib.PROPERTY_OVERWRITE) == 1
    assert kvlc.getProperty(kvlclib.PROPERTY_CHANNEL_MASK) == 1
    n_new_file_name = 0
    while True:
        try:
            kvlc.convertEvent()
            if kvlc.IsOutputFilenameNew():
                n_new_file_name += 1
                print("New output filename: %s" % kvlc.getOutputFilename())
                print("About %d events left to convert..." % kvlc.eventCount())
        except kvlclib.KvlcEndOfFile:
            assert kvlc.IsOverrunActive() == 0
            if kvlc.IsOverrunActive():
                print("NOTE! The extracted data contained overrun.")
                kvlc.resetOverrunActive()

            assert kvlc.IsDataTruncated() == 0
            if kvlc.IsDataTruncated():
                print("NOTE! The extracted data was truncated.")
                kvlc.resetStatusTruncated()
            break

    of = kvlc.getOutputFilename()
    kvlc.flush()
    assert n_new_file_name == 1
    assert int(os.path.getsize(of)) > 0


def test_writer_formats():
    """Test one property"""
    fmt = kvlclib.WriterFormat(kvlclib.FILE_FORMAT_PLAIN_ASC)
    assert fmt.isPropertySupported(kvlclib.PROPERTY_CHANNEL_MASK)
    print(
        "Default value for CHANNEL_MASK is %s"
        % bin(fmt.getPropertyDefault(kvlclib.PROPERTY_CHANNEL_MASK))
    )
