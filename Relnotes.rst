===========================================================================
                            Release Notes
===========================================================================
This is the release notes for the pycanlib module.

.. contents::
    :depth: 2


New Features and Fixed Problems in V1.28.675  (26-NOV-2024)
===========================================================================
* Minor changes.


New Features and Fixed Problems in V1.27.606  (18-SEP-2024)
===========================================================================
* Minor changes.


New Features and Fixed Problems in V1.26.487  (22-MAY-2024)
===========================================================================
* Added new enums to canlib.


New Features and Fixed Problems in V1.25.393  (18-FEB-2024)
===========================================================================
* Minor changes.


New Features and Fixed Problems in V1.24.935  (13-SEP-2023)
===========================================================================
* Minor changes.


New Features and Fixed Problems in V1.23.804  (05-MAY-2023)
===========================================================================
* `.canlib`:

  - Added support for time domains `~canlib.canlib.TimeDomain`.


New Features and Fixed Problems in V1.22.565  (08-SEP-2022)
===========================================================================
* `.canlib`:

  - Added support for object buffers `.canlib.objbuf`.


New Features and Fixed Problems in V1.21.463  (29-MAY-2022)
===========================================================================

* General:

  - Added CAN FD versions of examples:

    - :ref:`pinger_example` (:ref:`pinger_fd_example`), and
    - :ref:`dbmonitor_example` (:ref:`dbmonitor_fd_example`).

* `.canlib`:

  - Added exceptions `.canlib.CanTimeout` and `.canlib.CanOverflowError`.

  - Added new bitrate constant `~.canlib.BitrateFD.BITRATE_2M_60P`.

  - Added support for `.canlib.MessageFlag.LOCAL_TXACK`. This requires CANlib
    SDK v5.39 or newer.

  - Checking for `.canlib.MessageFlag.OVERRUN` using ``in`` will now return
    ``True`` if either `~.canlib.MessageFlag.SW_OVERRUN` or
    `~.canlib.MessageFlag.HW_OVERRUN` is set.

* `.kvadblib`:

  - Added read only property `.kvadblib.Message.canflags` which returns
    relevant ``VFrameFormat`` attributes converted into `.canlib.MessageFlag`
    (e.g. the J1939 ``VFrameFormat`` attribute does not have a corresponding
    flag and is excluded).

  - `.kvadblib.Message.asframe()` now include CAN FD flags on the returned
    `~canlib.Frame`. Note that this requires CANlib SDK v5.39 or newer.


New Features and Fixed Problems in V1.20.360  (15-FEB-2022)
===========================================================================
* General:

  - Python 3.10 is now officially supported.

  - Fixed `canlib.connected_devices()` to ignore removed devices, instead of
    raising an exception.

  - Added `.canlib.exceptions.CanGeneralError` to documentation, noting that
    this should *not* be caught explicitly.

  - Extracted tutorial sample code into standalone files, updated bus
    parameters in CAN FD code to work with U100.

* `.canlib`:

  - Removed internal attribute `Channel.flags`, use
    `.canlib.ChannelData.channel_flags` instead.

  - Corrected return value of `~canlib.canlib.Channel.is_can_fd` when channel
    was opened explicitly using `~canlib.canlib.Open.NO_INIT_ACCESS`. Now
    also always returns a `bool`.

  - Added `.ChannelData.bus_param_limits` (wraps canCHANNELDATA_BUS_PARAM_LIMITS)

  - Added t Programming chapter to documentation.

  - Corrected name of bitrate constant inside table in "Set CAN Bitrate" chapter.

* `.linlib`:

  - Deprecated `~.linlib.Channel.getCanHandle`, use `~.linlib.Channel.get_can_channel`
    instead.

* `.kvlclib`:

  - `.kvlclib.WriterFormat.getPropertyDefault` and
    `.kvlclib.ReaderFormat.getPropertyDefault` now returns `None` if property do
    not support get/set, as e.g. `~.kvlclib.Property.SIGNAL_BASED`.
  - Added support for experimental format KME60
  - Clarified usage of `.kvlclib.Converter.addDatabaseFile()`.

* `.kvadblib`:

  - Added support for Attribute Definition of type HEX,
    `.kvadblib.AttributeType.HEX`.
  - Comment and Unit on a signal now converts cp1252 coding to utf-8.
  - Added support for experimental format KME60


New Features and Fixed Problems in V1.19.205  (13-SEP-2021)
===========================================================================
* General:

  - Updated docstrings, mainly of lower level classes.
  - Modernized code, mainly conversions to f-strings.

* `.canlib.dllLoader`:

  - Setting the environment variable `READTHEDOCS` == `True` inhibits loading
    of shared libraries. Used e.g. when building documentation on ReadTheDocs.

* `.canlib.kvamemolibxml`:

  - The functions `~canlib.kvamemolibxml.xmlGetLastError`,
    `~canlib.kvamemolibxml.xmlGetValidationWarning` and
    `~canlib.kvamemolibxml.xmlGetValidationError` now returns enum classes when
    possible.

* `.canlib.kvrlib`:

    - Minor readability updates for `kvrDeviceInfo.__str__`

New Features and Fixed Problems in V1.18.846  (25-MAY-2021)
===========================================================================
* `.canlib.canlib`:

  - Added LEDs 4 through 11 to `canlib.canlib.LEDAction` (needs CANlib v5.19+).

* `.canlib.kvadblib`:

  - Default value of EnumAttribute is now returned as `int`
  - Added wrapper for kvaDbGetMsgByPGNEx

* `.canlib.kvlclib`:

  - Added wrapper for kvlcFeedLogEvent

* Added `canlib.j1939` module for some j1939 helpers.


New Features and Fixed Problems in V1.17.748  (16-FEB-2021)
===========================================================================
* `.canlib.canlib`:

  - Corrected `~canlib.canlib.Channel.set_bus_params_tq` regarding type of flag
    attribute.
  - Added support for using `~canlib.canlib.Channel.setBusParams` and
    `~canlib.canlib.Channel.getBusParams` for channels that were opened using
    `~canlib.canlib.busparams.BusParamsTq`.
  - Added `~canlib.canlib.Bitrate` and `~canlib.canlib.BitrateFD` enums for use with
    `~canlib.canlib.Channel.setBusParams` and `~canlib.canlib.openChannel`.
    `canlib.canBITRATE_xxx` and `canlib.canFD_BITRATE_xxx` constants are still
    supported but deprecated.
  - Added enum member BITRATE_8M_80P to `~canlib.canlib.BitrateFD` and constant
    canlib.canFD_BITRATE_8M_80P.

* `.canlib.kvlclib`

  - Added exception `~canlib.kvlclib.KvlcFileExists`.


New Features and Fixed Problems in V1.16.588  (09-SEP-2020)
===========================================================================
* `.canlib.canlib`:

  - Added support for new bus parameter API in CANlib v.5.34. See section
    :ref:`set_can_bitrate` for more information.
  - Added attributes to `canlib.IOControl.__dir__` and
    `canlib.ChannelData.__dir__` in order to better support auto completion
    in IDEs.
  - Deprecated `canlib.Device.channel`, use
    `canlib.Device.open_channel` instead, which correctly handles
    keyword arguments
  - Added new Open flag `canlib.canlib.Open.NOFLAG` for parameter `flags`.

* `.canlib.kvadblib`:

  - Corrected `~canlib.kvadblib.Dbc.interpret` when looking for CAN messages
    with extended id.
  - Updated `~canlib.kvadblib.Dbc.get_message` so that it requires
    `~canlib.kvadblib.MessageFlags.EXT` (bit 31) to be set on `id` if using
    extended id:s.
  - Added a new argument `flags` to `~canlib.kvadblib.Dbc.get_message_by_id`.
    If using messages with extended id:s, `~canlib.kvadblib.MessageFlags.EXT`
    should be set on `flags`.

* `.canlib.kvlclib`:

  - The `file_format` parameter in `canlib.kvlclib.Converter.setInputFile` now
    accepts `~canlib.kvlclib.ReaderFormat` as well.
  - Added a newer version of the BLF format, now also with CAN FD support
    'canlib.kvlclib.FileFormat.VECTOR_BLF_FD'. The format has both read and write
    capabilities.


New Features and Fixed Problems in V1.15.483  (27-MAY-2020)
===========================================================================
* Dropped support for v2.7, v3.4 and v3.5, added v3.7 and v3.8.


New Features and Fixed Problems in V1.14.428  (02-APR-2020)
===========================================================================
* Minor changes.


New Features and Fixed Problems in V1.13.390  (24-FEB-2020)
===========================================================================
* `.canlib.canlib`:

  - Added `~canlib.canlib.HandleData` to wrap canGetHandleData. Also added
    `~canlib.canlib.Channel.channel_data` as a helper function.

  - IOControl now returns utf-8 decoded strings instead of "bytes in string".

  - Fixed a bug where `~canlib.canlib.Device.isconnected` would return `False`
    if the `channel_number` attribute was larger than the total number of
    available CANlib channels, regardles of if the device was connected or not.

* `.canlib`:

  - Corrected `~canlib.Frame` comparison (!=) with other types, e.g. None


New Features and Fixed Problems in V1.12.251  (08-OCT-2019)
===========================================================================
* Minor changes.


New Features and Fixed Problems in V1.11.226  (13-SEP-2019)
===========================================================================
* `canlib.canlib`:

  - Added a slight delay in get_bus_statistics because the underlying
    functions in CANlib are asynchronous.

  - Added `~canlib.canlib.Channel.read_error_counters` and `iocontrol`
    `clear_error_counters`.

  - Added `~canlib.canlib.Channel.getBusOutputControl`.

  - Added `~canlib.canlib.Channel.fileDiskFormat` that formats the disk in a
    remote device, i.e Kvaser DIN Rail.

* `canlib.BoundSignal.value`:

  - If the signal is an enum-signal, and the signal's value is not found in the
    enum definition, the raw value is now returned.

* `canlib.kvmlib`:

  - Marked using kvmlib class as deprecated (was deprecated in v1.6)

  - Replaced `~canlib.kvmlib.Kme.estimate_events` with
    `.Kme.event_count_estimation` in order to have same name as
    `.LogFile.event_count_estimation`. Old function name is now deprecated.

  - When found, new 64 bit version of the dll call, `kvmLogFileMountEx`,
    `kvlcEventCountEx`, and `kvmKmeCountEventsEx` (added in CANlib v5.29), is
    now used.

  - Added `~canlib.kvmlib.LogFile.log_type` for supporting the different log
    types generated by Kvaser Memorator Light HS v2.

* `canlib.kvadblib`:

  - `~canlib.kvadblib.Dbc` raises `~canlib.kvadblib.exception.KvdDbFileParse`
    if the dbc file loaded contains syntax errors.


New Features and Fixed Problems in V1.10.102  (12-MAY-2019)
===========================================================================
* Reference documentation has been restructured.

* `~canlib.canlib.Channel`:

  - Added support for slicing environment variables declared as char.  Replaced
    low level function `scriptEnvvarSetData` with
    `~canlib.canlib.Channel.script_envvar_set_data` and added
    `~canlib.canlib.envvar.DataEnvVar` which is now returned when a char envvar is
    returned.

* `canlib.kvadblib`:

  - Error messages from the CAN database parser in `~canlib.kvadblib.Dbc` can be
    retrieved using `~canlib.kvadblib.get_last_parse_error()`.


New Features and Fixed Problems in V1.9.909  (03-MAR-2019)
===========================================================================
* `canlib.kvadblib`:

  - Error texts are now fetched from the dll using kvaDbGetErrorText().

* `canlib.kvlclib`:

  - Added support for DLC mismatch handling included in CANlib v5.27

* `canlib.kvDevice`:

  - The `canlib.kvDevice.kvDevice` class is now deprecated, use `canlib.Device`
    instead

* `canlib.Device`:

  - Added method `Device.issubset` as a helper to find loosely specified
    devices.

* `canlib.canlib.iopin`:

  - Added attributes `fw_version` and `serial` to `IoPin`. To read these
    attributes, CANlib v5.27 is needed.

  - `AddonModule` is a new class, holding attributes of one add-on module.

  - `Config.modules` is now an attribute, calculated at creation time and
    containing an ordered list of `AddonModule` objects. The old functionality
    has been moved to `Config._modules`

  - `Config.issubset` is a new method to identify if a configuration contains
    the expected add-on modules.


New Features and Fixed Problems in V1.8.812  (26-NOV-2018)
===========================================================================
* `canlib.canlib`:

  - Fixed issue were Channel.handle attribute would not be initialized when
    opening of the channel failed.

  - Added experimental support for accessing IO-pins on sub modules of the
    Kvaser DIN Rail SE 400S that was added to CANlib v5.26. This includes a
    new module `canlib.canlib.iopin`.

* `canlib.kvadblib`:

  - Fixed issue with signals were multiplexing mode, and scaling (factor and
    offset) returned wrong values from a loaded .dbc file.
  - Added show_all argument to Dbc.messages. Dbc.__iter__ now set show_all to
    False in order to skip VECTOR__INDEPENDENT_SIG_MSG messages.


New Features and Fixed Problems in V1.7.741  (16-SEP-2018)
===========================================================================
* `canlib.kvmlib`:

  - Added `canlib.kvmlib.event_count_estimation`
  - Added `canlib.kvmlib.kme`
    Previous kvmlib.kmeXXX functions are now deprecated.

* `canlib.canlib`:

  - Added `canlib.canlib.ScriptStatus`
  - Added enums to `canlib.canlib.ChannelCap`
  - Fixed `canlib.canlib.canWriteSync`

* `canlib.kvlclib`:

  - Added API to access information about reader formats.
  - Added kvlclib.Property to replace old
    PROPERTY_XXX constants which are now deprecated.
  - Added kvlclib.reader_formats and kvlclib.writer_formats to replace now
    deprecated kvlclib.WriterFormat.getFirstWriterFormat and
    kvlclib.WriterFormat.getNextWriterFormat.


New Features and Fixed Problems in V1.6.615  (13-MAY-2018)
===========================================================================

* Updated for CANlib SDK v5.23.

* Getting version numbers should now be done with ``dllversion()``,
  which will return `canlib.BetaVersionNumber` if the dll is marked as Beta.
  Also added ``canlib.prodversion()`` to return the CANlib product version number.

* `canlib.device`:

  - New `canlib.device.Device` class (available as `canlib.Device`) that is a
    simpler version of kvDevice. `canlib.device.Device` objects can be defined
    using an EAN and serial number, or a connected device can be searched for
    using `canlib.device.Device.find`. These objects do not require the device
    to stay connected, and can be used to later create most other `canlib`
    objects, e.g. `canlib.canlib.Channel`, `canlib.kvmlib.Memorator`, etc.

  - New `canlib.device.connected_devices` which returns an iterator of
    `canlib.device.Device` objects, one for each device currently connected.

* `canlib.ean`:

  - `canlib.ean.EAN` objects can be tested for equality, both with other
    `canlib.ean.EAN` objects and with strings.

  - Added `CanNotFound` exception.

  - `canlib.ean.EAN` objects can now be directly instantiated from string,
    i.e. ``ean = canlib.EAN(ean_string)`` instead of ``ean =
    canlib.EAN.from_string(ean_string)``.

  - `canlib.ean.EAN` objects can be converted back into any of the
    representations that can be used to create them. See the documentation of
    `canlib.ean.EAN` for more info.

  - `canlib.ean.EAN` objects can be indexed and iterated upon, yielding the
    digits as `int`\s.

* `canlib.canlib`:

  - `canlib.canlib.EnvVar` object raises `EnvvarNameError` when given an
    illegal name, instead of `AssertionError`.

  - `canlib.canlib.openChannel` can now set the bitrate of the channel opened.

  - `canlib.canlib.Channel` objects automatically close their handles when
    garbage collected

  - `canlib.canlib.Channel` has new methods
    `canlib.canlib.Channel.scriptRequestText` and
    `canlib.canlib.Channel.scriptGetText` to get text printed with
    ``printf()`` by a script. This text is returned as a
    `canlib.canlib.ScriptText` object.

* `canlib.kvamemolibxml`:

  - A new, object oriented way of dealing with kvamemolibxml using
    `canlib.kvamemolibxml.Configuration` objects.

* `canlib.kvmlib`:

  - Improved object model

    + New `canlib.kvmlib.openDevice` function that returns a
      `canlib.kvmlib.Memorator` object representing a connected Memorator
      device. See the documentation of `canlib.kvmlib.Memorator` for
      instructions on how to use this new class to more easily interface with
      your Memorators.

    + New `canlib.kvmlib.openKmf` function for opening .KMF files that returns
      a `canlib.kvmlib.Kmf` object that is similar to
      `canlib.kvmlib.Memorator`. See the docstring of `canlib.kvmlib.Kmf` for
      more information.

* `canlib.linlib`:

  - Getting version number with `canlib.linlib.dllversion` (requires CANlib SDK
    v5.23 or newer).

  - Explicit `canlib.linlib.Channel.close` function for forcing a linlib
    channel's internal handle to be closed.

* `canlib.canlib`:

  - Added support for accessing information within compiled t program (.txe) files.

    + Added wrapper function for `kvScriptTxeGetData`.
    + Added compiled t program (.txe) interface class `canlib.canlib.Txe`.

* `canlib.kvadblib`:

  - enums now returns non-empty dictionary in attribute definition returned
    from `EnumDefinition.definition`


New Features and Fixed Problems in V1.5.525  (12-FEB-2018)
===========================================================================

* Updated for CANlib SDK v5.22.

* Added support for LIN bus API (LINlib)

* Added support for Database API (kvaDbLib)
  Needs version v5.22 of CANlib SDK to get supported dll.

Restructuring of code in order to make the API simpler and the code base more
maintainable have resulted in the following changes (old style is deprecated,
shown in details while running Python with the -Wd argument):

* `canlib.kvMessage` has been renamed `canlib.Frame`

  - `canlib.Frame` objects are now accepted and returned when writing and reading channels.
  - The new `canlib.kvadblib` module uses these `canlib.Frame` objects heavily.

* `canlib.canlib`:

  - Added wrapper functions for `canReadStatus` and `canRequestChipStatus`
  - Deprecated use of `canlib.canlib.canlib()` objects; all methods have been moved to the module.

    + See the docstring of `canlib.canlib.CANLib` for more information

  - Simplified the names of the channel-classes (old names are deprecated):

    + The channel class is now `canlib.canlib.Channel`, instead of `canlib.canChannel`.
    + `canlib.canlib.ChannelData_Channel_Flags` is now `canlib.canlib.ChannelFlags`
    + `canlib.canlib.ChannelData_Channel_Flags_bits` is now `canlib.canlib.ChannelFlagBits`

  - `canlib.canlib.Channel` now uses `canlib.Frame` objects for reading and writing.

    + `canlib.Channel.read` now returns a `canlib.Frame` object instead of a tuple. However, `canlib.Frame` objects are largely compatible with tuples.
    + `canlib.Channel.write` takes a single argument, a `canlib.Frame` object. The previous call signature has been taken over by `canlib.Channel.write_raw`.
    + Likewise for `canlib.Channel.writeWait` and its new friend `canlib.Channel.writeWait_raw`.

  - The class `canlib.canlib.canVersion` has been removed, and
    `canlib.canlib.getVersion` now returns a `canlib.VersionNumber`. The new
    class still supports conversion to string and accessing ``.major`` and
    ``.minor`` attributes.

* `canlib.kvmlib`:

  - Added wrapper functions for kvmKmeReadEvent.
  - Corrected encoding for Python 3 in kmeOpenFile().
  - Deprecated names for several classes to make them more logical and more pythonic:

    + `canlib.kvmlib.memoMsg` is now `canlib.kvmlib.LogEvent`
    + `canlib.kvmlib.logMsg` is now `canlib.kvmlib.MessageEvent`
    + `canlib.kvmlib.rtcMsg` is now `canlib.kvmlib.RTCEvent`
    + `canlib.kvmlib.trigMsg` is now `canlib.kvmlib.TriggerEvent`
    + `canlib.kvmlib.verMsg` is now `canlib.kvmlib.VersionEvent`

  - The class `canlib.kvmlib.kvmVersion` has been removed, and
    `canlib.kvmlib.KvmLib.getVersion` now returns a `canlib.VersionNumber`. The
    new class still supports conversion to string and accessing ``.major``,
    ``.minor``, and ``.build`` attributes.

* `canlib.kvlclib`:

  - Added method `canlib.kvlclib.addDatabaseFile` and helper object `canlib.kvlclib.ChannelMask`.

  - The `canlib.kvlclib.KvlcLib` object has been deprecated.

    + All functions that relate to converters have been moved to the more appropriately named `canlib.kvlclib.Converter`.

      - Some of these functions have been renamed:

        + `IsOutputFilenameNew`, `IsOverrunActive`, and `IsDataTruncated` have all had their initial "i" lower-cased, as the upper case "I" was an error.
        + `getPropertyDefault` and `isPropertySupported` are no longer available on the `Converter` object, they must be accessed via the `format` attribute::

            converter.format.getPropertyDefault(...)
    + `canlib.kvlclib.WriterFormat.getFirstWriterFormat` and `canlib.kvlclib.WriterFormat.getNextWriterFormat` now returns a `kvlclib.FileFormat` object (which is based on the `IntEnum` class).

    + Other functions have been moved to the `canlib.kvlclib` module.
    + `deleteConverter` is no longer supported. Instead, converters are automatically deleted when garbage collected. If their contents must be flushed to file, see the new `canlib.kvlclib.Converter.flush` method.

  - The class `canlib.kvlclib.KvlcVersion` has been removed, and
    `canlib.kvmlib.kvlclib.getVersion` now returns a `canlib.VersionNumber`. The
    new class still supports conversion to string and accessing ``.major``,
    ``.minor``, and ``.build`` attributes.


* `canlib.kvrlib`:

  - The `canlib.kvrlib.KvrLib` object has been deprecated; all methods have been moved to the module.

  - `canlib.kvrlib.getVersion` no longer returns a `canlib.kvrlib.kvrVersion`
    but a `canlib.VersionNumber`. The return value still supports conversion to
    string and accessing ``.major`` and ``.minor`` attributes.

* `canlib.kvamemolibxml`:

  - Renamed from `canlib.KvaMemoLibXml`, however trying to import the old name will just import the new one instead.
  - Deprecated the use of `canlib.kvamemolibxml.KvaMemoLib` objects, all methods have been moved to the `canlib.kvamemolibxml` module itself.
  - Breaking change: Moved values that were incorrectly defined as constants into enums. In most cases this should not have any impact, as all the values are internal error codes and are turned into Python exceptions. But if you nonetheless use the kvamemolibxml status values directly, you'll need to change your code as follows:

    + ``KvaXmlStatusERR_XXX_XXX`` is now ``Error.XXX_XXX``.
    + ``KvaXmlValidationStatusERR_XXX_XXX`` is now ``ValidationError.XXX_XXX``
    + ``KvaXmlValidationStatusWARN`` is now ``ValidationWarning.XXX_XXX``.
    + ``KvaXmlStatusFail`` is now ``Error.FAIL`` (Changed to be consistent with other KvaXmlStatus errors). The same is true for ``ValidationError.FAIL``.
    + ``KvaXmlStatusOK`` and ``KvaXmlValidationStatusOK`` are still treated as if they are constants, as they are not error statuses.

  - `canlib.kvamemolibxml.getVersion` no longer returns a string but a
    `canlib.VersionNumber`. The return value still supports conversion to
    string.

* Exceptions:

  - Exceptions throughout the package have been standardised, and now all inherit from `canlib.exceptions.CanlibException`.
  - The `canERR` attribute that some exceptions had has been deprecated in favour of a `status` attribute. Furthermore, all `canlib` exceptions now have this attribute; the status code that was returned from a C call that triggered the specific exception.


New Features and Fixed Problems in V1.4.373  (13-SEP-2017)
===========================================================================
* Minor changes.


New Features and Fixed Problems in V1.3.242  (05-MAY-2017)
===========================================================================
* Added missing unicode conversions for Python3.

* Linux

  - Added support for new libraries (kvadblib, kvmlib, kvamemolibxml, kvlclib).
  - Added wrappers KvFileGetCount, kvFileGetName, kvFileCopyXxxx, kvDeviceSetMode, kvDeviceGetMode

* canlib:

  - Added wrapper for kvFileDelete
  - Enhanced printout from canScriptFail errors.
  - Second file argument in fileCopyFromDevice and fileCopyToDevice is now optional.
  - OS now loads all dependency dll (also adding KVDLLPATH to PATH in Windows).


New Features and Fixed Problems in V1.2.163  (15-FEB-2017)
===========================================================================
* Added wrapper function canlib.getChannelData_Cust_Name()
* Added module canlib.kvlclib which is a wrapper for the Converter Library
  kvlclib in CANlib SDK.

* Added wrapper function canChannel.flashLeds().

* Added missing unicode conversions for Python3.

* Fixed bug where CANlib SDK install directory was not always correctly
  detected in Windows 10.


New Features and Fixed Problems in V1.1.23  (28-SEP-2016)
===========================================================================
* canSetAcceptanceFilter and kvReadTimer was not implemented in Linux


New Features and Fixed Problems in V1.0.10  (15-SEP-2016)
===========================================================================
* Initial module release.

* Added kvmlib.kmeSCanFileType()

* Added canChannel.canAccept() and canChannel.canSetAcceptanceFilter()



