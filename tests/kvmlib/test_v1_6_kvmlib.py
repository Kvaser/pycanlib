import filecmp
import os.path

from conftest import kvdeprecated

import canlib.kvmlib as kvmlib


# Read-write not working for ['logfile003.kme40', 'logfile003.kme25', 'logfile003.kme']
@kvdeprecated
def test_kme(datadir, tmpdir):
    ml_src = kvmlib.kvmlib()
    ml_dst = kvmlib.kvmlib()
    src_name = os.path.join(datadir, "short-burst", "logfile003.kme50")
    kme_type = kvmlib.kvmFILE_KME50
    dst_name = tmpdir.join("test_kme_creation.kmeX")

    ml_src.kmeOpenFile(str(src_name), filetype=kme_type)
    ml_dst.kmeCreateFile(str(dst_name), filetype=kme_type)
    num_events = ml_src.kmeCountEvents()
    print('{} contains about {} events.'.format(src_name, num_events))
    for i in range(num_events):
        logevent = ml_src.kmeReadEventLogFormat()
        if logevent is None:
            break
        print(logevent)
        ml_dst.kmeWriteEvent(logevent)

    assert filecmp.cmp(src_name, src_name, shallow=False)
    # Currently does not work
    # assert filecmp.cmp(src_name, dst_name, shallow=False)
    ml_src.kmeCloseFile()
    ml_dst.kmeCloseFile()
