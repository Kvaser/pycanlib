Convert a .kme50 file to plain ASCII
####################################

.. literalinclude:: /../examples/convert_kme_asc.py


Description
===========

We have created a wrapper function `try_set_propery` that will examine the property we are trying to set, and ignore the setting if the current format used does not support the property. While converting events in the `convert_events` function, we also inform the user if any overruns or data truncation was detected.


Sample Output
=============

.. highlight:: console

::

   C:\example>python convert_kme_asc.py gensig.kme50
   Output filename is 'C:\example\gensig.txt'
     Property.SIZE_LIMIT is supported (Default: 0)
       Current value: 100
     Property.OVERWRITE is supported (Default: 0)
       Current value: 1
     Property.WRITE_HEADER is supported (Default: 0)
       Current value: 1
     Property.LIMIT_DATA_BYTES is supported (Default: 64)
       Current value: 8
   Converting about 310 events...
   New output filename: 'C:\example\gensig-part0.txt
   About 309 events left...
