canlib
######

.. toctree::
   :maxdepth: 2


.. contents::

The following sections contain sample code for inspiration on how to use Kvaser Python canlib.


List connected devices
----------------------

.. literalinclude:: /../examples/list_devices.py


Sample Output:

.. highlight:: console

::

    CANlib Channel: 0
    Card Number   : 7
    Device        : Kvaser Memorator Pro 2xHS v2 (channel 0)
    Driver Name   : kcany7a
    EAN           : 73-30130-00819-9
    Firmware      : 3.24.0.722
    Serial Number : 12330
    CANlib Channel: 2
    Card Number   : 8
    Device        : Kvaser Memorator Pro 5xHS (channel 0)
    Driver Name   : kcany8a
    EAN           : 73-30130-00832-8
    Firmware      : 3.23.0.646
    Serial Number : 10028
    CANlib Channel: 7
    Card Number   : 0
    Device        : Kvaser Virtual CAN Driver (channel 0)
    Driver Name   : kcanv0a
    EAN           : 00-00000-00000-0
    Firmware      : 0.0.0.0
    Serial Number : 0


.. highlight:: python


Send and receive single frame
-----------------------------

.. literalinclude:: /../examples/send_and_receive_can.py



Send and receive CAN FD frame
-----------------------------

.. literalinclude:: /../examples/send_and_receive_canfd.py

