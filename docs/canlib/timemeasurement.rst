Time Measurement
================

CAN messages are time stamped as they arrive. This time stamping is, depending
on your hardware platform, done either by the CAN interface hardware or by
CANlib.

In the former case, the accuracy is pretty good, in the order of 1 - 10
microseconds; when CANlib does the job, the accuracy is more like 100
microseconds to 10 milliseconds and you may experience a rather large
jitter. This is because Windows is not a real-time operating system.

Use `.Channel.readTimer` to read the current time, the return value is the
current time using the clock of that channel.


Accuracy
--------

The accuracy of the time stamps depends on the hardware.

The members of the Kvaser Leaf family have an onboard CPU. The time stamp
accuracy varies (check the hardware manual) but the high-end members have very
precise time stamping. The accuracy can be as good as one microsecond depending
on the hardware. If more than one Leaf is used, their clocks are automatically
kept in sync by the Kvaser MagiSync™ technology.

Other CAN interfaces, like the Kvaser Leaf, LAPcan and USBcan II, have an
on-board CPU and clock and provide very accurate time stamps for incoming CAN
messages. The accuracy is typically 10-20 microseconds.

Certain interfaces, like the PCIcan (PCI) series of boards, don't have an
on-board CPU so the driver relies on the clock in the PC to timestamp the
incoming messages. As Windows is not a real-time operating system, this gives
an accuracy which is in the order of one millisecond.


Resolution
----------

The resolution of the time stamps is, by default, 1 ms. It can be changed to a
better resolution if desired.

Use `.IOControl` attribute `~canlib.canlib.IOControl.timer_scale` to change the
resolution of the time stamps, if desired. This will not affect the accuracy of
the time stamps.

