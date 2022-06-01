.. _dbmonitor_example:

Monitor Channel Using CAN Database
##################################

.. literalinclude:: /../examples/dbmonitor.py


Description
===========

Any CAN messages received on the specified channel will be looked up in the
database using `~canlib.kvadblib.Dbc.interpret`, which allows the script to
print the "phys" value of each signal instead of just printing the raw data (as
:doc:`./monitor` does). The script also prints the message's name and
comment (if available), as well as the signals name and unit.


Sample Output
=============

.. highlight:: console

::

   ┏ EngineData
   ┃ PetrolLevel: 0.0 l
   ┃ EngPower: 12.0 kW
   ┃ EngForce: 0.0 N
   ┃ IdleRunning: 0.0
   ┃ EngTemp: -30.0 °C
   ┃ EngSpeed: 7735.0 rpm
   ┗
   ┏ GearBoxInfo
   ┃ EcoMode: 0.0
   ┃ ShiftRequest: 0.0
   ┃ Gear: 0.0
   ┗
   ┏ EngineData
   ┃ PetrolLevel: 0.0 l
   ┃ EngPower: 28.0 kW
   ┃ EngForce: 0.0 N
   ┃ IdleRunning: 0.0
   ┃ EngTemp: -30.0 °C
   ┃ EngSpeed: 3467.0 rpm
   ┗
   ┏ GearBoxInfo
   ┃ EcoMode: 1.0
   ┃ ShiftRequest: 0.0
   ┃ Gear: 0.0
   ┗
   ┏ EngineData
   ┃ PetrolLevel: 0.0 l
   ┃ EngPower: 0.0 kW
   ┃ EngForce: 0.0 N
   ┃ IdleRunning: 0.0
   ┃ EngTemp: -50.0 °C
   ┃ EngSpeed: 1639.0 rpm
   ┗
   ┏ GearBoxInfo
   ┃ EcoMode: 1.0
   ┃ ShiftRequest: 0.0
   ┃ Gear: 1.0
   ┗
   ┏ EngineData
   ┃ PetrolLevel: 60.0 l
   ┃ EngPower: 0.0 kW
   ┃ EngForce: 0.0 N
   ┃ IdleRunning: 0.0
   ┃ EngTemp: 142.0 °C
   ┃ EngSpeed: 0.0 rpm
   ┗
   ┏ GearBoxInfo
   ┃ EcoMode: 0.0
   ┃ ShiftRequest: 0.0
   ┃ Gear: 0.0
   ┗
   ┏ EngineData
   ┃ PetrolLevel: 172.0 l
   ┃ EngPower: 51.0 kW
   ┃ EngForce: 0.0 N
   ┃ IdleRunning: 0.0
   ┃ EngTemp: -50.0 °C
   ┃ EngSpeed: 0.0 rpm
   ┗
   ┏ GearBoxInfo
   ┃ EcoMode: 0.0
   ┃ ShiftRequest: 0.0
   ┃ Gear: 0.0
   ┗

.. _dbmonitor_fd_example:

CAN FD version
==============

This example is basically the same as ``dbmonitor.py`` above, except we are now using CAN FD.

Note that you also need the ``dbmonitor.py`` file, next to ``dbmonitorfd.py`` below, since we are reusing the `monitor_channel` function.

.. highlight:: python

.. literalinclude:: /../examples/dbmonitorfd.py


