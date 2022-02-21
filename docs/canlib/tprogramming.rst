t Programming
=============

The Kvaser t programming language is event oriented and modeled after C. It can
be used to customize the behavior of the Kvaser Memorator v2 and other Kvaser t
capable devices.

A t program is invoked via hooks, which are entry points that are executed at
the occurrence of certain events. These events can be, for example, the arrival
of specific CAN messages, timer expiration, or external input.

Here we will describe how to interact with t programs on a Kvaser device
(i.e. loading, starting, stopping) For a complete reference to the t language,
see the `Kvaser t Programming Language
<https://www.kvaser.com/download/?utm_source=software&utm_ean=7330130980327&utm_status=latest>`_
available from https://www.kvaser.com/downloads.


Load and Unload t Program
-------------------------

The first step is to compile your t program into a .txe file, see the `Kvaser t
Programming Language
<https://www.kvaser.com/download/?utm_source=software&utm_ean=7330130980327&utm_status=latest>`_. A
compiled .txe file may be examined using `.Txe`::

  >>> t = canlib.Txe("HelloWorld.txe")
  >>> t.description
  'This is my hello world program.'

Before starting a t program you need to load it into an available "slot". Some
Kvaser devices have multiple slots, and are therefore capable of running
multiple programs simultaneously.

To load a t program located on the host PC, use
`.Channel.scriptLoadFile()`. The `.canlib.Channel` used determines the default channel
for the loaded t program. If your channel was opened to a device's second
channel, the default channel number will be set to 1 (the numbering of channel
on the card starts from 0). You can read this value using
`.Channel.channel_data.chan_no_on_card`


To load a t program located on the device, use
`.Channel.scriptLoadFileOnDevice()`. To copy arbitrary files to and from the
the device, use `.Channel.fileCopyToDevice()` and
`.Channel.fileCopyFromDevice()` respectively.

To unload a stopped script, use  `.Channel.scriptUnload()`.

You may use `.Channel.fileGetCount()`, and `.Channel.fileGetName()` to examine
files located on the Kvaser device, and `.Channel.fileDelete()` to delete a
specific file.

.. note::
   Not all Kvaser devices support storing t programs and other files locally on
   the device (i.e. USBcan Pro 2xHS v2). Please refer to your device's User
   Guide for more information. All User Guides may be downloaded from
   `www.kvaser.com/downloads
   <https://www.kvaser.com/download/#?categories=documentation>`_.


Start and Stop a t Program
--------------------------

To start a previously loaded t program, use `.Channel.scriptStart()`. You may
stop a running script using `.Channel.scriptStop()`. To examine the status of a
slot (i.e. if the slot is free or has a program loaded or running), use
`.Channel.scriptStatus()`.


Example
-------

The following code fragment shows how to load the compiled t program "HelloWorld.txe" from the PC, and then start and stop the t program::

  >>> from canlib import canlib
  >>> ch = canlib.openChannel(0)
  >>> ch.scriptLoadFile(slot=0, filePathOnPC="C:/dev/HelloWorld.txe")
  >>> ch.scriptStatus(slot=0)
  <ScriptStatus.LOADED: 1>
  >>> ch.scriptStart(slot=0)
  >>> ch.scriptStatus(slot=0)
  <ScriptStatus.RUNNING|LOADED: 3>
  >>> ch.scriptStop(slot=0)
  >>> ch.close()


Environment Variables
---------------------

To communicate between the PC and your t program, you can use t Environment
Variables (Envvar). When a t program has been loaded, the Envvar defined in the
t program can be accessed via `.Channel.envvar`, however the t program must be
running in order to be able to set the value of an Envvar.

There are three types of Envvar in t; `int`, `float`, and `char*`. The first
two are accessed as the corresponding Python type, and the last is accessed
using `.canlib.envvar.DataEnvVar` which behaves as an array of bytes.

If we have a t program, ``envvar.txe``, that set up three Envvar as follows::

  envvar
  {
    int   IntVal;
    float FloatVal;
    char  DataVal[512];
  }

  on start {
    envvarSetValue(IntVal, 0);
    envvarSetValue(FloatVal, 15.0);
    envvarSetValue(DataVal, "Fear not this night\nYou will not go astray");
  }

The following example starts the t program `envvar.txe` and acesses it's Envvar.

  >>> from canlib import canlib
  >>> ch = canlib.openChannel(0)
  >>> ch.scriptLoadFile(slot=0, filePathOnPC="envvar.txe")
  >>> ch.scriptStart(slot=0)
  >>> ch.envvar.IntVal
  0
  >>> ch.envvar.IntVal = 3
  >>> ch.envvar.IntVal
  3
  >>> ch.envvar.FloatVal
  15.0
  >>> ch.envvar.DataVal[9:20]
  b'this night\n'
  >>> ch.scriptStop(slot=0)
  >>> ch.close()

Note that setting of the Envvars has also been done in the t program. For
examples on how to use an Envvar in your t program, see the `Kvaser t
Programming Language
<https://www.kvaser.com/download/?utm_source=software&utm_ean=7330130980327&utm_status=latest>`_.


Send Event
----------

You may trigger the "on key" hook in your t program by sending a
``kvEVENT_TYPE_KEY`` to a running t program using
`.Channel.scriptSendEvent()`. The following will trigger an ``on key 'a'
{...}`` hook::

  >>> ch.scriptSendEvent(eventNo=ord('a'))
