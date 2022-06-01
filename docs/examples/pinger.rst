.. _pinger_example:

Send Random Messages on CAN Channel
###################################

.. literalinclude:: /../examples/pinger.py


Description
===========

.. note::
  There must be some process reading the messages for ``pinger.py`` to work
  (see e.g. :doc:`./dbmonitor`).

`ping_loop` will first extract a random list of messages (see :ref:`randomness`), and then enter a loop that creates a new `~canlib.kvadblib.FrameBox` before adding some random signals with random values (the quantity specified by the `quantity`/``--quantity`` argument).

Adding random signals is done with `set_random_framebox_signal`, which picks a random signal from the framebox, and `get_random_value` which inspects the given signal and provides a random value based on the signal's definition.

Finally, the loop pauses for `interval`/``--interval`` seconds between sending messages.


.. _randomness:

Randomness
----------

The random selection of messages is done with the `seed`/``--seed`` and `num_messages`/``num-messages`` arguments. If `num_messages` is ``-1``, all messages from the database will be used. Otherwise, `num_message` specifies the number of messages to be randomly picked from the database.

The `seed` argument will be sent to `random.seed` before the messages are
selected (which is done with `random.sample`), which means as long as the seed
remains the same, the same messages are selected. The `seed` can also be set to
``None`` for a pseudo-random seed.


Sample Output
=============

.. highlight:: console

::

  Randomly selecting signals from the following messages:
  [Message(name='EngineData', id=100, flags=<MessageFlag.0: 0>, dlc=8, comment=''), Message(name='GearBoxInfo', id=1020, flags=<MessageFlag.0: 0>, dlc=1, comment='')]
  Seed used was '0'

  Sending frame Frame(id=1020, data=bytearray(b'\x00'), dlc=1, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=100, data=bytearray(b'\x00\x00\x16]\x00\x00\x00\x00'), dlc=8, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=1020, data=bytearray(b'\x00'), dlc=1, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=100, data=bytearray(b'\x00\x00\x00\xdd\x00\x00\x00\x00'), dlc=8, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=1020, data=bytearray(b'\x00'), dlc=1, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=100, data=bytearray(b'\x00\x00\x00\xe0\x00\x00`\t'), dlc=8, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=1020, data=bytearray(b'\x04'), dlc=1, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=100, data=bytearray(b'f\x07\n\x00\x00\x00\x00\x00'), dlc=8, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=1020, data=bytearray(b'\x00'), dlc=1, flags=<MessageFlag.0: 0>, timestamp=None)
  Sending frame Frame(id=100, data=bytearray(b'\x0c\x15-\x00\x00\x00\x00\x00'), dlc=8, flags=<MessageFlag.0: 0>, timestamp=None)

.. _pinger_fd_example:

CAN FD version
==============

This example is basically the same as ``pinger.py`` above, except we are now using CAN FD.

Note that you also need the ``pinger.py`` file, next to ``pingerfd.py`` below, since we are reusing the `ping_loop` function.

.. highlight:: python

.. literalinclude:: /../examples/pingerfd.py
