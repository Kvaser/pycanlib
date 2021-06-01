j1939
=====

.. toctree::
   :maxdepth: 2


.. automodule:: canlib.j1939


Protocol Data Units
~~~~~~~~~~~~~~~~~~~

.. autoclass:: canlib.j1939.Pdu
    :members:
    :undoc-members:

.. autoclass:: canlib.j1939.Pdu1
    :members:
    :undoc-members:

.. autoclass:: canlib.j1939.Pdu2
    :members:
    :undoc-members:

Converting CAN Id
~~~~~~~~~~~~~~~~~

For a j1939 message, the CAN identifier is divided into the following fields:

+----------+-----------+-----------+--------+----------+---------+
|          | Extended  |           | PDU    | PDU      | Source  |
| Priority | Data Page | Data Page | Format | Specific | Address |
+==========+===========+===========+========+==========+=========+
| 3 bit    | 1 bit     | 1 bit     | 8 bit  | 8 bit    | 8 bit   |
+----------+-----------+-----------+--------+----------+---------+

Use `pdu_from_can_id` and `can_id_from_pdu` to convert.


.. autofunction:: canlib.j1939.pdu_from_can_id

.. autofunction:: canlib.j1939.can_id_from_pdu
