kvrlib
######

.. toctree::
   :maxdepth: 2


.. contents::

The following sections contain sample code for inspiration on how to use Kvaser Python kvrlib.


Connect to your remote device
-----------------------------

.. literalinclude:: /../examples/connect_to_remote_device.py

.. highlight:: console

This results in the following::

    kvrlib version: 2070
    Connecting to device with serial number 10545
    Looking for device using addresses: 10.0.255.255:0 (IPV4_PORT)
    Scanning result:
    [
    name/hostname  : "MiMi-06348-000710" / "kv-06348-000710"
      ean/serial   : 73301-30006348 / 710
      fw           : 2.4.231
      addr/cli/AP  : 10.0.3.138 (IPV4) / 10.0.3.84 (IPV4) / - (UNKNOWN)
      availability : Availability.STORED|FOUND_BY_SCAN
      usage/access : DeviceUsage.FREE / Accessibility.PUBLIC
      pass/enc.key : yes / yes,
    name/hostname  : "TestClient1-2-DUT-01" / "swtdut01"
      ean/serial   : 73301-30006713 / 10545
      fw           : 3.4.822
      addr/cli/AP  : 10.0.3.54 (IPV4) / 10.0.3.98 (IPV4) / - (UNKNOWN)
      availability : Availability.STORED|FOUND_BY_SCAN
      usage/access : DeviceUsage.REMOTE / Accessibility.PUBLIC
      pass/enc.key : yes / yes]

    Connecting to the following device:
    ---------------------------------------------

    name/hostname  : "TestClient1-2-DUT-01" / "swtdut01"
      ean/serial   : 73301-30006713 / 10545
      fw           : 3.4.822
      addr/cli/AP  : 10.0.3.54 (IPV4) / 10.0.3.98 (IPV4) / - (UNKNOWN)
      availability : Availability.STORED|FOUND_BY_SCAN
      usage/access : DeviceUsage.REMOTE / Accessibility.PUBLIC
      pass/enc.key : yes / yes
