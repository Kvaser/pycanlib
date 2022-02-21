"""send_and_receive_canfd.py

Here are some minimal code to send and receive a CAN FD frame.

"""

from canlib import canlib, Frame

# Specifying an arbitration phase bus speed of 1 Mbit/s,
# and a data phase bus speed of 2 Mbit/s. See documentation
# for more information on how to set bus parameters.
params_arbitration = canlib.busparams.BusParamsTq(
    tq=40,
    phase1=8,
    phase2=8,
    sjw=8,
    prescaler=2,
    prop=23
)
params_data = canlib.busparams.BusParamsTq(
    tq=20,
    phase1=8,
    phase2=4,
    sjw=4,
    prescaler=2,
    prop=7
)

# open channel as CAN FD using the flag
ch0 = canlib.openChannel(channel=0, flags=canlib.Open.CAN_FD)
ch0.setBusOutputControl(drivertype=canlib.Driver.NORMAL)
ch0.set_bus_params_tq(params_arbitration, params_data)
ch0.busOn()

ch1 = canlib.openChannel(channel=1, flags=canlib.Open.CAN_FD)
ch1.setBusOutputControl(drivertype=canlib.Driver.NORMAL)
ch1.set_bus_params_tq(params_arbitration, params_data)
ch1.busOn()

# set FDF flag to send using CAN FD
# set BRS flag to send using higher bit rate in the data phase
frame = Frame(
    id_=100,
    data=range(32),
    flags=canlib.MessageFlag.FDF | canlib.MessageFlag.BRS
)
print('Sending', frame)
ch0.write(frame)

frame = ch1.read(timeout=1000)
print('Received', frame)

ch0.busOff()
ch1.busOff()
