from enum import IntEnum

from canlib import canlib


# Change back 2 january 2020.. Doesn't work in python 2.7
# def start_script(script_fp, ch, slot, *, out=False, err=False, info=False):
def start_script(script_fp, ch, slot, out=False, err=False, info=False):
    print("loading script...")
    ch.scriptLoadFile(slot, script_fp)
    print("Requesting text...")
    ch.scriptRequestText(slot)
    ch.scriptRequestText(slot + 0x20000000)
    ch.scriptRequestText(slot + 0x30000000)
    ch.scriptRequestText(slot, canlib.ScriptRequest.UNSUBSCRIBE)
    print("Starting script...")
    ch.scriptStart(slot)


def stop_script(ch, slot):
    status = ch.scriptStatus(slot)
    if canlib.enums.ScriptStatus.LOADED in status:
        if canlib.enums.ScriptStatus.RUNNING in status:
            ch.scriptStop(slot)
        ch.scriptUnload(slot)

class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    ERROR = 2
    CRITICAL = 3


class ScriptRunner:
    def __init__(self, channel_number, script_fp, slot=0):
        self.channel_number = channel_number
        # os.fspath is only supported in python 3.6+
        # self.script_fp = os.fspath(script_fp)

        self.script_fp = script_fp.decode() if type(script_fp) == bytes else str(script_fp)

        self.slot = slot

        self.ch = None

    def __enter__(self):
        self.ch = canlib.openChannel(self.channel_number)
        stop_script(self.ch, self.slot)
        start_script(self.script_fp, self.ch, self.slot, out=True, err=True, info=True)
        self.envvar = canlib.EnvVar(self.ch)

        return self

    def __exit__(self, *args, **kwargs):
        stop_script(self.ch, self.slot)
        self.ch.close()

    def __repr__(self):
        text = 'ScriptRunner({c}, {t}, slot={s}'.format(
            c=self.channel_number, t=self.script_fp, s=self.slot
        )
        return text

    def lines(self):
        try:
            while True:
                text = self.ch.scriptGetText()
                yield text
        except canlib.CanNoMsg:
            return

    def pad(self, data, name):
        """Return data left-padded with null bytes to fill envvar named name"""
        size = len(getattr(self.envvar, name))
        return data.ljust(size, b'\0')

    def print_output(self):
        print("  SCRIPT OUTPUT:")
        for line in self.lines():
            print('    ' + line.rstrip('\n'))
        print("  END OF SCRIPT OUTPUT")
