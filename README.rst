canlib - a Python wrapper for Kvaser CANlib



Supported Libraries and Installation
====================================

The Python canlib module wraps the Kvaser CANlib API in order to make it easy to control most aspects of any Kvaser CAN interface. For more information about Kvaser please go to https://www.kvaser.com/.

The latest version of this package is available on the `Kvaser Download page <https://www.kvaser.com/downloads-kvaser/>`_ (`pycanlib.zip <https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130981911&utm_status=latest>`_).

Supported platforms
-------------------
Windows and Linux using Python v3.6+ (both 32 and 64 bit).


Supported libraries
-------------------
The following libraries are currently supported:

=============  ====================  ===================  =====================
 Library        Module                Windows              Linux
=============  ====================  ===================  =====================
CANlib         canlib.canlib         canlib32.dll         libcanlib.so
kvaMemoLibXML  canlib.kvamemolibxml  kvaMemoLibXML.dll    libkvamemolibxml.so
kvrlib         canlib.kvrlib         kvrlib.dll,          not supported
                                     irisdll.dll,
                                     irisflash.dll,
                                     libxml2.dll
kvmlib         canlib.kvmlib         kvaMemoLib0600.dll,  not supported, [2]_
                                     kvaMemoLib0700.dll,  libkvamemolib0700.so,
                                     kvaMemoLib.dll,      libkvamemolib.so,
                                     kvmlib.dll           libkvmlib.so
kvlclib        canlib.kvlclib        kvlclib.dll [1]_     libkvlclib.so
kvaDbLib       canlib.kvadblib       kvaDbLib.dll         libkvadblib.so
LINlib         canlib.linlib         linlib.dll           liblinlib.so
=============  ====================  ===================  =====================

.. [1] The kvlclib.dll depends on dll files from matlab wich are installed alongside kvlclib.dll.
.. [2] The kvaMemoLib0600.dll, which supports older devices, is not supported under Linux.

Installation
------------
Install the Python package from `PyPI <https://pypi.org/project/canlib/>`_ using e.g. ``pip``:

.. code-block:: shell

    $ pip install canlib

If you have downloaded the package zip file from the `Kvaser Download page <https://www.kvaser.com/downloads-kvaser/>`_, first unzip ``pycanlib.zip``. Then navigate to the unzipped pycanlib using the command line. It should contain the file ``canlib-x.y.z-py2.py3-none-any.whl``, where x,y,z are version numbers.
Run the following command:

.. code-block:: shell

    $ pip install canlib-x.y.z-py2.py3-none-any.whl

The Kvaser CANlib DLLs or shared libraries also need to be installed:

Windows
^^^^^^^
On **Windows**, first install the ``canlib32.dll`` by downloading and installing "Kvaser Drivers for Windows" which can be found on the `Kvaser Download page <https://www.kvaser.com/downloads-kvaser/>`_ (`kvaser_drivers_setup.exe <https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130980013&utm_status=latest>`_) This will also install ``kvrlib.dll``, ``irisdll.dll``, ``irisflash.dll`` and ``libxml2.dll`` used by kvrlib.

The "Kvaser CANlib SDK" also needs to be downloaded from the same place (`canlib.exe <https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130980150&utm_status=latest>`_) and installed if more than just CANlib will be used. This will install the rest of the supported library dll's.

The two packages, "Kvaser Drivers for Windows" and "Kvaser CANlib SDK", contains both 32 and 64 bit versions of the included dll's.


Linux
^^^^^
On **Linux**, first install the ``libcanlib.so`` by downloading and installing "Kvaser LINUX Driver and SDK" which can be found on the `Kvaser Download page <https://www.kvaser.com/downloads-kvaser/>`_ (`linuxcan.tar.gz <https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130980754&utm_status=latest>`_).


If more than just CANlib will be used, the rest of the supported libraries will be available by downloading and installing "Linux SDK library" (`kvlibsdk.tar.gz <https://www.kvaser.com/downloads-kvaser/?utm_source=software&utm_ean=7330130981966&utm_status=latest>`_).


Usage
-----

Example of using canlib to list some information about connected Kvaser devices:

.. code-block:: Python

        from canlib import canlib

        num_channels = canlib.getNumberOfChannels()
        print(f"Found {num_channels} channels")
        for ch in range(num_channels):
            chd = canlib.ChannelData(ch)
            print(f"{ch}. {chd.channel_name} ({chd.card_upc_no} / {chd.card_serial_no})")


Which may result in:

.. code-block:: shell

        Found 4 channels
        0. Kvaser Memorator Pro 2xHS v2 (channel 0) (73-30130-00819-9 / 12330)
        1. Kvaser Memorator Pro 2xHS v2 (channel 1) (73-30130-00819-9 / 12330)
        2. Kvaser Virtual CAN Driver (channel 0) (00-00000-00000-0 / 0)
        3. Kvaser Virtual CAN Driver (channel 1) (00-00000-00000-0 / 0)

..
   .. code-block:: Python

           >>> from canlib import canlib
           >>> canlib.getNumberOfChannels()
           4
           >>> for ch in range(canlib.getNumberOfChannels()):
           ...     chd = canlib.ChannelData(ch)
           ...     print(f"{ch}. {chd.channel_name} ({chd.card_upc_no} / {chd.card_serial_no})")
           0. Kvaser Memorator Pro 2xHS v2 (channel 0) (73-30130-00819-9 / 12330)
           1. Kvaser Memorator Pro 2xHS v2 (channel 1) (73-30130-00819-9 / 12330)
           2. Kvaser Virtual CAN Driver (channel 0) (00-00000-00000-0 / 0)
           3. Kvaser Virtual CAN Driver (channel 1) (00-00000-00000-0 / 0)


Support
-------

You are invited to visit the Kvaser web pages at https://www.kvaser.com/support/. If you don't find what you are looking for, you can obtain support on a time-available basis by sending an e-mail to support@kvaser.com.

Bug reports, contributions, suggestions for improvements, and similar things are much appreciated and can be sent by e-mail to support@kvaser.com.


What's new
----------
A complete set of release notes are available in the package documentation included in the zip file available at the `Kvaser Download page <https://www.kvaser.com/downloads-kvaser/>`_.


Links
-----

  * Kvaser CANlib SDK Page: https://www.kvaser.com/developer/canlib-sdk/
  * Description of CANlib SDK library contents: https://www.kvaser.com/developer-blog/get-hardware-kvaser-sdk-libraries/


License
-------
This project is licensed under the terms of the MIT license.
