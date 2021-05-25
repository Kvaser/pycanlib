from conftest import kvdeprecated

import canlib.canlib as canlib


@kvdeprecated
def test_list_devices():
    cl = canlib.canlib()
    num_channels = cl.getNumberOfChannels()
    print("Found %d channels" % num_channels)
    for ch in range(0, num_channels):
        print(
            "%d. %s (%s / %s)"
            % (
                ch,
                cl.getChannelData_Name(ch),
                cl.getChannelData_EAN(ch),
                cl.getChannelData_Serial(ch),
            )
        )
