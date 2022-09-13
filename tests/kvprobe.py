# -*- coding: utf-8 -*-

from collections import namedtuple

from canlib import canlib, Frame
from canlib.canlib.enums import LoggerType
from canlib.canlib.exceptions import CanNotImplementedError

can = []
canfd = []
lin = []
virtual = []
logger_v2 = []
local_r = []
remote = []
script = []
iopin = []
objbuf = []
can_node_map = {}


def header():
    header = '\n'.join(
        [
            "┏━ Using kvprobe",
            "┃ CAN channels: " + str(can),
            "┃ CAN FD channels: " + str(canfd),
            "┃ LIN channels: " + str(lin),
            "┃ virtual channels: " + str(virtual),
            "┃ logger v2 channels: " + str(logger_v2),
            "┃ script channels: " + str(script),
            "┃ iopin_channels: " + str(iopin),
            "┃ local_r: " + str(local_r),
            "┃ remote: " + str(remote),
            "┃ objbuf: " + str(objbuf),
            "┗",
        ]
    )
    return header


for n in range(canlib.getNumberOfChannels()):
    chd = canlib.ChannelData(n)

    can.append(n)

    capabilities = chd.channel_cap & chd.channel_cap_mask
    if canlib.ChannelCap.IO_API & capabilities:
        iopin.append(n)
    if canlib.ChannelCap.SCRIPT & capabilities:
        script.append(n)
    if canlib.ChannelCap.LOGGER & capabilities and chd.logger_type not in {
        LoggerType.NOT_A_LOGGER,
        LoggerType.V1,
    }:
        logger_v2.append(n)
    if canlib.ChannelCap.CAN_FD & capabilities:
        canfd.append(n)

    if canlib.ChannelCap.REMOTE_ACCESS & capabilities:
        if chd.is_remote:
            remote.append(n)
        else:
            local_r.append(n)

    hwtype = chd.card_type
    if hwtype is canlib.HardwareType.CANLINHYBRID:
        lin.append(n)
    if hwtype is canlib.HardwareType.VIRTUAL:
        virtual.append(n)
        can.remove(n)  # virtual channels don't have all capabilities of CAN

    with canlib.Channel(n, flags=canlib.Open.ACCEPT_VIRTUAL) as ch:
        try:
            buf = ch.allocate_periodic_objbuf(1000, Frame(100, b''))
            buf.free()
            objbuf.append(n)
        except CanNotImplementedError:
            pass


def generate_can_node_map():
    frame = Frame(100, data=b'0')
    channels = []
    try:
        for n in can:
            ch = canlib.Channel(n, flags=canlib.Open.REQUIRE_INIT_ACCESS)
            channels.append(ch)
            ch.setBusParams(canlib.canBITRATE_1M)
            ch.busOn()
        for ch_a_no, ch_a in enumerate(channels):
            listeners = []
            try:
                ch_a.writeWait(frame, 20)
            except canlib.CanTimeout:
                pass

            for ch_b_no, ch_b in enumerate(channels):
                try:
                    ch_b.read()
                except canlib.CanNoMsg:
                    continue
                if ch_b_no != ch_a_no:
                    listeners.append(ch_b_no)
            can_node_map[ch_a_no] = listeners
    finally:
        for ch in channels:
            ch.close()

generate_can_node_map()

def can_communicate_with(a, b):
    if a in can_node_map:
        return b in can_node_map[a]
    if b in can_node_map:
        return a in can_node_map[b]
    return False


FeatureNames = namedtuple(
    "FeatureNames", "can canfd lin virtual logger_v2 local_r remote script iopin"
)

features = FeatureNames(
    can=can,
    canfd=canfd,
    lin=lin,
    virtual=virtual,
    logger_v2=logger_v2,
    local_r=local_r,
    remote=remote,
    script=script,
    iopin=iopin,
)
