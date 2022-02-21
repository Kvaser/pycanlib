"""send_and_receive_can.py

Here is some basic code to send and receive a single frame.

"""


from canlib import canlib, Frame
from canlib.canlib import ChannelData


def setUpChannel(channel=0,
                 openFlags=canlib.Open.ACCEPT_VIRTUAL,
                 outputControl=canlib.Driver.NORMAL):
    ch = canlib.openChannel(channel, openFlags)
    print("Using channel: %s, EAN: %s" % (ChannelData(channel).channel_name,
                                          ChannelData(channel).card_upc_no))
    ch.setBusOutputControl(outputControl)
    # Specifying a bus speed of 250 kbit/s. See documentation
    # for more informationon how to set bus parameters.
    params = canlib.busparams.BusParamsTq(
        tq=8,
        phase1=2,
        phase2=2,
        sjw=1,
        prescaler=40,
        prop=3
    )
    ch.set_bus_params_tq(params)
    ch.busOn()
    return ch


def tearDownChannel(ch):
    ch.busOff()
    ch.close()


print("canlib version:", canlib.dllversion())
ch0 = setUpChannel(channel=0)
ch1 = setUpChannel(channel=1)
frame = Frame(
    id_=100,
    data=[1, 2, 3, 4],
    flags=canlib.MessageFlag.EXT
)
ch1.write(frame)
while True:
    try:
        frame = ch0.read()
        print(frame)
        break
    except canlib.canNoMsg:
        pass
    except canlib.canError as ex:
        print(ex)
tearDownChannel(ch0)
tearDownChannel(ch1)
