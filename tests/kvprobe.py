# -*- coding: utf-8 -*-

from collections import namedtuple

from canlib import canlib
from canlib.canlib.enums import LoggerType

can = []
canfd = []
lin = []
virtual = []
logger_v2 = []
local_r = []
remote = []
script = []
iopin = []


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
