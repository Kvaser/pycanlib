Monitor a Channel
#################

.. literalinclude:: /../examples/monitor.py


Description
===========

Any CAN frames received on the specified channel will be printed. Note that the
signals contained in the frame is not be extracted, only the raw data is
printed. To extract the signals, see :doc:`./dbmonitor`.


Sample Output
=============

.. highlight:: console

::

   Listening...
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 1020
   data: b'\x00'
   flags: MessageFlag.STD
   timestamp: 939214
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 100
   data: b'\xd1\x06\x00\x19\x00\x00\x18\x15'
   flags: MessageFlag.STD
   timestamp: 939215
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 1020
   data: b'\x01'
   flags: MessageFlag.STD
   timestamp: 939417
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 100
   data: b'\x00\x00\x00\x19\x00\x00\xc82'
   flags: MessageFlag.STD
   timestamp: 939418
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 1020
   data: b'\x00'
   flags: MessageFlag.STD
   timestamp: 939620
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 100
   data: b'\x00\x00\x00\x00\x00\x00\x903'
   flags: MessageFlag.STD
   timestamp: 939621
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 1020
   data: b'@'
   flags: MessageFlag.STD
   timestamp: 939823
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 100
   data: b')\x03\x17\xf5\x00\x00\x00\x00'
   flags: MessageFlag.STD
   timestamp: 939824
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 1020
   data: b'\x02'
   flags: MessageFlag.STD
   timestamp: 940026
   ════════════════════════════════════ Frame received ═════════════════════════════════════
   id: 100
   data: b'\x1b\x0eC\x00\x00\x00\x00\x00'
   flags: MessageFlag.STD
   timestamp: 940027
