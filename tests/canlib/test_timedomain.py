import pytest
import time

from timeit import default_timer as timer

from canlib import canlib, Frame
from canlib.canlib import TimeDomain


def test_add_remove(chA, chB):
    """
    chA, chB: With or without magisync

    Check data of empty time domain
    - Exp all zero values in TimeDomainData

    Add channels to time domain
     - Exp a sync group if any MagiSync capable members
     - Exp som of MagiSync capable members and non capable member == 2
     - Exp any MagiSync Devices if and only if any MagiSync members

    Remove channels from time domain
     - Exp all zero values

    """

    with TimeDomain() as domain:
        data = domain.get_data()
        assert data.sync_groups == 0
        assert data.synced_members == 0
        assert data.non_sync_cards == 0
        assert data.non_synced_members == 0

        domain.add_channel(chA)
        domain.add_channel(chB)

        data = domain.get_data()
        print(data)
        # 1 group if synced members is non-zero
        assert data.sync_groups == (not not data.synced_members)
        assert data.synced_members + data.non_synced_members == 2

        # either both zero or both non-zero
        assert (not not data.non_sync_cards) == (not not data.non_synced_members)

        domain.remove_channel(chA)
        domain.remove_channel(chB)

        data = domain.get_data()
        assert data.sync_groups == 0
        assert data.synced_members == 0
        assert data.non_sync_cards == 0
        assert data.non_synced_members == 0


def test_reset_time(chA, chB):
    """
    Sender chA, reciever chB: With or without magisync

    Reset time on reciever, sleep 100 ms, send frame
     - Exp timestamp >= 100 ms

    Reset time on reciever, dont sleep 0 ms, send frame
     - Exp timestamp < 100 ms
    """

    chA.busOn()
    chB.busOn()

    with TimeDomain() as domain:
        domain.add_channel(chB)

        data = domain.get_data()
        assert data.synced_members + data.non_synced_members == 1

        domain.reset_time()
        time.sleep(0.100) # s

        frameA = Frame(id_=4, data=b'')
        chA.write(frameA)
        t0 = timer()

        frameB = chB.read(timeout=100) # ms
        tB = timer() -t0

        assert frameB.id == frameA.id
        assert frameB.timestamp >= 100 # ms

        domain.reset_time()

        chA.write(frameA)
        t0 = timer()

        frameB = chB.read(timeout=100) # ms
        tB = timer() -t0

        assert frameB.id == frameA.id
        assert frameB.timestamp < 100 # ms

    chA.busOff()
    chB.busOff()