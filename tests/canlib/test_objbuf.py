from contextlib import contextmanager

import pytest

from canlib import canlib, Frame
from canlib.canlib import objbuf


MAX_NUM_RESPONSE_BUFFERS = 8
MAX_NUM_PERIODIC_BUFFERS = 31


def test_message_filter():
    """Verify that MessageFilter correctly simulates the code, mask filter."""
    code = 0b0000_1010_0101_1111
    mask = 0b0000_1111_0000_0001
    id_0 = 0b1010_1010_1010_0001
    id_1 = 0b0000_1010_0000_0000
    msg_filter = objbuf.MessageFilter(code=code, mask=mask)
    assert msg_filter(id_0)
    assert not msg_filter(id_1)

@pytest.fixture(scope="module")
def chA_no(kvprobe):
    """Return an object buffer capable channel with atleast one listener."""
    objbuf = [n for n in kvprobe.objbuf if kvprobe.can_node_map[n] and n not in kvprobe.virtual]
    if not objbuf:
        pytest.skip()
    return objbuf[0]


@pytest.fixture()
def chA(chA_no):
    with canlib.Channel(chA_no, flags=canlib.Open.REQUIRE_INIT_ACCESS) as ch:
        ch.setBusParams(canlib.canBITRATE_1M)
        yield ch


@pytest.fixture()
def chB(kvprobe, chA_no):
    with canlib.Channel(kvprobe.can_node_map[chA_no][0], flags=canlib.Open.REQUIRE_INIT_ACCESS) as ch:
        ch.setBusParams(canlib.canBITRATE_1M)
        yield ch


def test_response_objbuf_allocate_all(chA):
    """We should be able to allocate exactly MAX_NUM_RESPONSE_BUFFERS object buffers."""
    # Allocate all available object buffers
    with pytest.raises(canlib.CanOutOfMemory):
        for i in range(100):
            _ = chA.allocate_response_objbuf(filter=None, frame=None)
    assert i == MAX_NUM_RESPONSE_BUFFERS


def test_periodic_objbuf_allocate_all(chA):
    """We should be able to allocate exactly MAX_NUM_PERIODIC_BUFFERS object buffers."""
    # Allocate all available object buffers
    with pytest.raises(canlib.CanOutOfMemory):
        for i in range(100):
            _ = chA.allocate_periodic_objbuf(period_us=1_000_000, frame=None)
    assert i == MAX_NUM_PERIODIC_BUFFERS


def test_response_closed_handle(chA):
    """Response buffers should not be available using a closed handle."""
    frame = Frame(id_=333, data=[1, 2, 3, 4, 5, 6])
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    response_buffer = chA.allocate_response_objbuf(filter=None, frame=None)
    response_buffer.set_filter(msg_filter)
    response_buffer.set_frame(frame)
    response_buffer.set_rtr_only(False)
    chA.close()
    with pytest.raises(canlib.CanInvalidHandle):
        response_buffer.set_filter(msg_filter)
    with pytest.raises(canlib.CanInvalidHandle):
        response_buffer.set_frame(frame)
    with pytest.raises(canlib.CanInvalidHandle):
        response_buffer.set_rtr_only(True)


def test_periodic_closed_handle(chA):
    """Periodic buffers should not be available using a closed handle."""
    frame = Frame(id_=333, data=[1, 2, 3, 4, 5, 6])
    periodic_buffer = chA.allocate_periodic_objbuf(period_us=1000, frame=None)
    periodic_buffer.set_frame(frame)
    periodic_buffer.set_msg_count(11)
    chA.close()
    with pytest.raises(canlib.CanInvalidHandle):
        periodic_buffer.set_period(1000)
    with pytest.raises(canlib.CanInvalidHandle):
        periodic_buffer.set_frame(frame)
    with pytest.raises(canlib.CanInvalidHandle):
        periodic_buffer.set_msg_count(11)


@pytest.mark.xfail(reason="Windows: Using unallocated response buffer does not return error.")
def test_response_set_unallocated(chA):
    """An unallocated response buffer should not be usable."""
    unallocated_buffer = canlib.objbuf.Response(chA)
    idx = unallocated_buffer.idx
    unallocated_buffer.free()
    unallocated_buffer.idx = idx
    unallocated_buffer.ch = chA
    with pytest.raises(canlib.CanError):
        unallocated_buffer.enable()
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6])
    with pytest.raises(canlib.CanError):
        unallocated_buffer.set_frame(frame)
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    with pytest.raises(canlib.CanError):
        unallocated_buffer.set_filter(msg_filter)
    with pytest.raises(canlib.CanError):
        unallocated_buffer.set_rtr_only(True)


def test_periodic_set_unallocated(chA):
    """An unallocated periodic buffer should not be usable."""
    unallocated_buffer = canlib.objbuf.Periodic(chA, period_us=1000)
    idx = unallocated_buffer.idx
    unallocated_buffer.free()
    unallocated_buffer.idx = idx
    unallocated_buffer.ch = chA
    with pytest.raises(canlib.CanError):
        unallocated_buffer.enable()
    with pytest.raises(canlib.CanError):
        unallocated_buffer.set_period(100_000)
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6])
    with pytest.raises(canlib.CanError):
        unallocated_buffer.set_frame(frame)
    with pytest.raises(canlib.CanError):
        unallocated_buffer.set_msg_count(11)
    with pytest.raises(canlib.CanError):
        unallocated_buffer.send_burst(length=2)


def test_objbuf_free_all(chA):
    """Call to canObjBufFreeAll() should make all object buffers available again."""
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6])
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    object_buffers = []
    # Allocate all available object buffers
    for i in range(MAX_NUM_RESPONSE_BUFFERS):
        object_buffers.append(chA.allocate_response_objbuf(filter=msg_filter, frame=frame))
    for i in range(MAX_NUM_PERIODIC_BUFFERS):
        object_buffers.append(chA.allocate_periodic_objbuf(period_us=1_000_000, frame=frame))

    # Free all object buffers
    chA.free_objbuf()

    # Allocate all available object buffers
    for i in range(MAX_NUM_RESPONSE_BUFFERS):
        object_buffers.append(chA.allocate_response_objbuf(filter=msg_filter, frame=frame))
    for i in range(MAX_NUM_PERIODIC_BUFFERS):
        object_buffers.append(chA.allocate_periodic_objbuf(period_us=1_000_000, frame=frame))


def test_response_objbuf_allocate_all_free_one(chA):
    """Allocate all response buffers, free one in the middle, reallocate the one freed."""
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6])
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    response_buffers = []

    # Allocate all available object buffers
    for i in range(MAX_NUM_RESPONSE_BUFFERS):
        response_buffers.append(chA.allocate_response_objbuf(filter=msg_filter, frame=frame))

    # Free one object buffer
    idx = response_buffers[2].idx
    response_buffers[2].free()
    assert response_buffers[2].idx == -1

    # Re-allocate the freed buffer
    response_buffer = chA.allocate_response_objbuf(filter=msg_filter, frame=frame)
    assert response_buffer.idx == idx


def test_periodic_objbuf_allocate_all_free_one(chA):
    """Allocate all periodic buffers, free one in the middle, reallocate the one freed."""
    periodic_buffers = []

    # Allocate all available object buffers
    for i in range(MAX_NUM_PERIODIC_BUFFERS):
        periodic_buffers.append(chA.allocate_periodic_objbuf(period_us=1_000_000, frame=None))

    # Free one object buffer
    idx = periodic_buffers[2].idx
    periodic_buffers[2].free()
    assert periodic_buffers[2].idx == -1

    # Re-allocate the freed buffer
    periodic_buffer = chA.allocate_periodic_objbuf(period_us=1_000_000, frame=None)
    assert periodic_buffer.idx == idx


def test_periodic_objbuf_allocate_all_free_one_send(chA, chB):
    """Allocate all periodic buffers, free one in the middle, reallocate the one freed.
    Now send one message from all buffers (with unique CAN ID) and verify CAN ID.

    """
    PERIOD_MS = 200
    PERIOD_PLUS_MS = PERIOD_MS + 100
    periodic_buffers = []
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6], flags=canlib.MessageFlag.STD)

    # Allocate all available object buffers
    for i in range(MAX_NUM_PERIODIC_BUFFERS):
        frame.id = 200 + i
        periodic_buffers.append(chA.allocate_periodic_objbuf(period_us=1_000_000, frame=frame))

    # Free one object buffer
    idx = periodic_buffers[2].idx
    periodic_buffers[2].free()
    assert periodic_buffers[2].idx == -1

    # Re-allocate the freed buffer
    frame.id = 302
    periodic_buffers[2] = chA.allocate_periodic_objbuf(period_us=PERIOD_MS * 1000, frame=frame)
    assert periodic_buffers[2].idx == idx

    chA.busOn()
    chB.busOn()
    for b in periodic_buffers:
        b.set_msg_count(1)
        b.enable()
    for i in range(MAX_NUM_PERIODIC_BUFFERS):
        msg = chB.read(timeout=PERIOD_PLUS_MS)
        expected_id = 200 + i
        if i == 2:
            expected_id = 302
        assert msg.id == expected_id
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_PLUS_MS))


def test_periodic_objbuf_send_burst(chA, chB):
    """Manually send a burst of periodic buffer messages."""
    PERIOD_MS = 200
    PERIOD_PLUS_MS = PERIOD_MS + 100
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6], flags=canlib.MessageFlag.STD)
    periodic_buffer = chA.allocate_periodic_objbuf(period_us=PERIOD_MS * 1000, frame=frame)
    chA.busOn()
    chB.busOn()
    burst_len = 4
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read())
    periodic_buffer.send_burst(length=burst_len)
    for i in range(burst_len):
        msg = chB.read(timeout=PERIOD_PLUS_MS)
        assert msg == frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_PLUS_MS))


def test_response_objbuf_enable_trigger(chA, chB):
    """When enabled, a response should be returned when CAN ID matches the filter."""
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    response_frame = Frame(id_=200, data=[], flags=canlib.MessageFlag.STD)
    response_buffer = chA.allocate_response_objbuf(filter=msg_filter, frame=response_frame)
    can_id = 5  # This CAN id should trigger a response
    assert msg_filter(can_id)
    frame = Frame(id_=can_id, data=[1, 2, 3, 4, 5, 6], flags=canlib.MessageFlag.STD)
    response_buffer.enable()
    chA.busOn()
    chB.busOn()
    chB.write(frame)
    msg = chA.read(timeout=200)
    assert msg == frame
    msg = chB.read(timeout=200)
    assert msg == response_frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=200))


def test_response_objbuf_disable_trigger(chA, chB):
    """When disabled, no response should be returned even if CAN ID matches the filter."""
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    response_frame = Frame(id_=200, data=[], flags=canlib.MessageFlag.STD)
    response_buffer = chA.allocate_response_objbuf(filter=msg_filter, frame=response_frame)
    can_id = 5  # This CAN id should trigger a response
    assert msg_filter(can_id)
    frame = Frame(id_=can_id, data=[1, 2, 3, 4, 5, 6], flags=canlib.MessageFlag.STD)
    response_buffer.enable()
    response_buffer.disable()
    chA.busOn()
    chB.busOn()
    chB.write(frame)
    msg = chA.read(timeout=200)
    assert msg == frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=200))


def test_periodic_objbuf_enable_disable(chA, chB):
    """Periodic messages should be sent when the periodic buffer is enabled,
    nothing should be sent when disabled.

    """
    PERIOD_MS = 200
    PERIOD_PLUS_MS = PERIOD_MS + 100
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6], flags=canlib.MessageFlag.STD)
    periodic_buffer = chA.allocate_periodic_objbuf(period_us=PERIOD_MS * 1000, frame=frame)
    chA.busOn()
    chB.busOn()
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_PLUS_MS))
    periodic_buffer.enable()
    msg = chB.read(timeout=PERIOD_PLUS_MS)
    assert msg == frame
    msg = chB.read(timeout=PERIOD_PLUS_MS)
    assert msg == frame
    periodic_buffer.disable()
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_PLUS_MS))


def test_response_objbuf_enable_not_trigger(chA, chB):
    """When enabled, a response should not be returned when the CAN ID does not match the filter."""
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    response_frame = Frame(id_=200, data=[], flags=canlib.MessageFlag.STD)
    response_buffer = chA.allocate_response_objbuf(filter=msg_filter, frame=response_frame)
    can_id = 6  # This CAN id should not trigger a response
    assert not msg_filter(can_id)
    frame = Frame(id_=can_id, data=[1, 2, 3, 4, 5, 6], flags=canlib.MessageFlag.STD)
    response_buffer.enable()
    chA.busOn()
    chB.busOn()
    chB.write(frame)
    msg = chA.read(timeout=200)
    assert msg == frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=200))


def test_response_objbuf_rtr_only_trigger(chA, chB):
    """When the response buffer flag is set to AUTO_RESPONSE_RTR_ONLY enabled, a
    response should be returned when both the CAN ID filter matches and the
    message has the RTR flag set.

    """
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    response_frame = Frame(id_=200, data=[], flags=canlib.MessageFlag.STD)
    response_buffer = chA.allocate_response_objbuf(filter=msg_filter, frame=response_frame, rtr_only=True)
    can_id = 5  # This CAN id should trigger a response
    assert msg_filter(can_id)
    frame = Frame(id_=can_id, data=[0, 0, 0, 0, 0, 0], flags=canlib.MessageFlag.STD | canlib.MessageFlag.RTR)
    response_buffer.enable()
    chA.busOn()
    chB.busOn()
    chB.write(frame)
    msg = chA.read(timeout=200)
    assert msg == frame
    msg = chB.read(timeout=200)
    assert msg == response_frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=200))


def test_response_objbuf_rtr_only_not_trigger(chA, chB):
    """When the response buffer flag is set to AUTO_RESPONSE_RTR_ONLY enabled, a
    response should not be returned when the CAN ID filter matches and the
    message does not have the RTR flag set.

    """
    msg_filter = objbuf.MessageFilter(code=0b01, mask=0b11)
    response_frame = Frame(id_=200, data=[], flags=canlib.MessageFlag.STD)
    response_buffer = chA.allocate_response_objbuf(filter=msg_filter, frame=response_frame, rtr_only=True)
    can_id = 5  # This CAN id should trigger a response
    assert msg_filter(can_id)
    frame = Frame(id_=can_id, data=[0, 0, 0, 0, 0, 0], flags=canlib.MessageFlag.STD)
    response_buffer.enable()
    chA.busOn()
    chB.busOn()
    chB.write(frame)
    msg = chA.read(timeout=200)
    assert msg == frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=200))


def test_periodic_objbuf_msg_count(chA, chB):
    """canObjBufSetMsgCount() can be used to limit the total number of sent messages."""
    PERIOD_MS = 200
    PERIOD_PLUS_MS = PERIOD_MS + 100
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6], flags=canlib.MessageFlag.STD)
    periodic_buffer = chA.allocate_periodic_objbuf(period_us=PERIOD_MS * 1000, frame=frame)
    chA.busOn()
    chB.busOn()
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_PLUS_MS))
    msg_count = 3
    periodic_buffer.set_msg_count(msg_count)
    periodic_buffer.enable()
    for i in range(msg_count):
        msg = chB.read(timeout=PERIOD_PLUS_MS)
        assert msg == frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_MS * 2))


def test_periodic_objbuf_msg_count_zero(chA, chB):
    """canObjBufSetMsgCount() can be used to limit the total number of sent messages."""
    PERIOD_MS = 200
    PERIOD_PLUS_MS = PERIOD_MS + 100
    frame = Frame(id_=200, data=[1, 2, 3, 4, 5, 6], flags=canlib.MessageFlag.STD)
    periodic_buffer = chA.allocate_periodic_objbuf(period_us=PERIOD_MS * 1000, frame=frame)
    chA.busOn()
    chB.busOn()
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_PLUS_MS))
    msg_count = 3
    periodic_buffer.set_msg_count(msg_count)
    periodic_buffer.enable()
    for i in range(msg_count):
        msg = chB.read(timeout=PERIOD_PLUS_MS)
        assert msg == frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_PLUS_MS))
    # Now reuse previous msg_count
    assert periodic_buffer.count == msg_count
    periodic_buffer.enable()
    for i in range(msg_count):
        msg = chB.read(timeout=PERIOD_PLUS_MS)
        assert msg == frame
    with pytest.raises(canlib.CanNoMsg):
        print(chB.read(timeout=PERIOD_MS * 2))
