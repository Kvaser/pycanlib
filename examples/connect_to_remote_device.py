"""connect_to_remote_device.py

Use the discovery functions to scan and connect to a remote device. Our remote
device has serial number 10545 and is already connected to the same network as our
computer.

"""
from canlib import kvrlib

SERIAL_NO = 10545

print("kvrlib version: %s" % kvrlib.getVersion())
print("Connecting to device with serial number %s" % SERIAL_NO)

addressList = kvrlib.kvrDiscovery.getDefaultAddresses(kvrlib.kvrAddressTypeFlag_BROADCAST)
print("Looking for device using addresses: %s" % addressList)
discovery = kvrlib.kvrDiscovery()
discovery.setAddresses(addressList)
deviceInfos = discovery.getResults()
print("Scanning result:\n%s" % deviceInfos)
# Connect to device with correct SERIAL_NO
for deviceInfo in deviceInfos:
    if deviceInfo.ser_no == SERIAL_NO:
        deviceInfo.connect()
        print('\nConnecting to the following device:')
        print('---------------------------------------------')
        print(deviceInfo)
        discovery.storeDevices(deviceInfos)
        break
discovery.close()
