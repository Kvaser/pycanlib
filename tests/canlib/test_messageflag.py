from canlib.canlib.enums import MessageFlag


def test_overrun_absent():
    flags = MessageFlag.FDF | MessageFlag.MSG_MASK
    assert MessageFlag.FDF in flags
    assert MessageFlag.OVERRUN not in flags
    assert MessageFlag.SW_OVERRUN not in flags
    assert MessageFlag.HW_OVERRUN not in flags


def test_overrun():
    flags = MessageFlag.OVERRUN
    assert MessageFlag.SW_OVERRUN in flags
    assert MessageFlag.HW_OVERRUN in flags
    assert MessageFlag.OVERRUN in flags


def test_sw_overrun():
    flags = MessageFlag.SW_OVERRUN
    assert MessageFlag.SW_OVERRUN in flags
    assert MessageFlag.HW_OVERRUN not in flags
    assert MessageFlag.OVERRUN in flags


def test_hw_overrun():
    flags = MessageFlag.HW_OVERRUN
    assert MessageFlag.SW_OVERRUN not in flags
    assert MessageFlag.HW_OVERRUN in flags
    assert MessageFlag.OVERRUN in flags
