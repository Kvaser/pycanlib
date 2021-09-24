Examine the Contents of a Database
##################################

.. literalinclude:: /../examples/examine_db.py


Description
===========

The script is structured into several generator functions that take a
`~canlib.kvadblib` object and yield lines of information about it. This allows
one function to add indentation to any other functions it uses.

Generally each function first yields information in the following order:

#. Any information about the object itself (e.g. ``db.flags`` and ``db.protocol``)

#. An empty string

#. For each type of sub-object (e.g. attribute definitions):

   #. A heading (e.g. ``'ATTRIBUTE_DEFINTIONS'``)

   #. For each object of that type (e.g. iterating through
      `~canlib.kvadblib.Dbc.attribute_definitions`):

      #. The objects name

      #. All lines from the ``*_lines`` function for the object type
         (e.g. `adef_lines`), with added indentation

   #. An empty string


Sample Output
=============

Running this script on the database created by :doc:`./create_db` gives the
following:

.. highlight:: console

::

   DATABASE
   engine_example
       flags: 0
       protocol: ProtocolType.CAN

       ATTRIBUTE DEFINITIONS
       BusType
           type: StringDefinition
           definition: DefaultDefinition(default='')
           owner: AttributeOwner.DB

       MESSAGES
       EngineData
           id: 100
           flags: MessageFlag.0
           dlc: 8
           comment:

           ATTRIBUTES

           SIGNALS
           PetrolLevel
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: -1
               size: ValueSize(startbit=24, length=8)
               scaling: ValueScaling(factor=1.0, offset=0.0)
               limits: ValueLimits(min=0.0, max=255.0)
               unit: l
               comment:

               ATTRIBUTES

           EngPower
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: -1
               size: ValueSize(startbit=48, length=16)
               scaling: ValueScaling(factor=0.01, offset=0.0)
               limits: ValueLimits(min=0.0, max=150.0)
               unit: kW
               comment:

               ATTRIBUTES

           EngForce
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: -1
               size: ValueSize(startbit=32, length=16)
               scaling: ValueScaling(factor=1.0, offset=0.0)
               limits: ValueLimits(min=0.0, max=0.0)
               unit: N
               comment:

               ATTRIBUTES

           IdleRunning
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: 0
               size: ValueSize(startbit=23, length=1)
               scaling: ValueScaling(factor=1.0, offset=0.0)
               limits: ValueLimits(min=0.0, max=0.0)
               unit:
               comment:

               ENUMERATIONS
               Running = 0
               Idle = 1

               ATTRIBUTES

           EngTemp
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: -1
               size: ValueSize(startbit=16, length=7)
               scaling: ValueScaling(factor=2.0, offset=-50.0)
               limits: ValueLimits(min=-50.0, max=150.0)
               unit: °C
               comment:

               ATTRIBUTES

           EngSpeed
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: -1
               size: ValueSize(startbit=0, length=16)
               scaling: ValueScaling(factor=1.0, offset=0.0)
               limits: ValueLimits(min=0.0, max=8000.0)
               unit: rpm
               comment:

               ATTRIBUTES


       GearBoxInfo
           id: 1020
           flags: MessageFlag.0
           dlc: 1
           comment:

           ATTRIBUTES

           SIGNALS
           EcoMode
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: -1
               size: ValueSize(startbit=6, length=2)
               scaling: ValueScaling(factor=1.0, offset=0.0)
               limits: ValueLimits(min=0.0, max=1.0)
               unit:
               comment:

               ATTRIBUTES

           ShiftRequest
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: 0
               size: ValueSize(startbit=3, length=1)
               scaling: ValueScaling(factor=1.0, offset=0.0)
               limits: ValueLimits(min=0.0, max=0.0)
               unit:
               comment:

               ENUMERATIONS
               Shift_Request_On = 1
               Shift_Request_Off = 0

               ATTRIBUTES

           Gear
               type: SignalType.UNSIGNED
               byte_order: SignalByteOrder.INTEL
               mode: 0
               size: ValueSize(startbit=0, length=3)
               scaling: ValueScaling(factor=1.0, offset=0.0)
               limits: ValueLimits(min=0.0, max=5.0)
               unit:
               comment:

               ENUMERATIONS
               Gear_5 = 5
               Gear_1 = 1
               Gear_3 = 3
               Idle = 0
               Gear_4 = 4
               Gear_2 = 2

               ATTRIBUTES




