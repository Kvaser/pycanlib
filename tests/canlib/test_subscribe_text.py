import os
import time

from tscript_wrap import ScriptRunner

from canlib import canlib

BITRATE = canlib.canBITRATE_1M
CHANNEL_FLAGS = 0


def test_subscribe(script_no, datadir):
    tscript_path = os.path.join(datadir, "txe", "text_subscribe.txe")
    print(tscript_path)
    with ScriptRunner(script_no, script_fp=tscript_path, slot=0) as envvar_t:
        time.sleep(5)
        envvar_t.print_output()
