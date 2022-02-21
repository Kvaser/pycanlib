"""list_devices.py -- List all connected CAN devices

This code probes each connected device and prints information about them.

"""

import canlib


for dev in canlib.connected_devices():
    print(dev.probe_info())
