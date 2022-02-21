Using canlib (CANlib)
=====================
The canlib module wraps the CAN bus API (CANlib), which is used to interact
with Kvaser CAN devices connected to your computer and the CAN bus. At its core
you have functions to set bus parameters (e.g. bit rate), go bus on/off and
read/write CAN messages. You can also use CANlib to download and start t
programs on supported devices.

.. toctree::

    introduction
    initialization
    devicesandchannels
    openchannel
    canframes
    sendandreceive
    buserrors
    timemeasurement
    usingthreads
    tprogramming
    iopinhandling
