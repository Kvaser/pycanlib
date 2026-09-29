import ctypes as ct
import os
import sys

from .. import VersionNumber, deprecation, dllLoader
from .dll import KvaMemoLibXmlDll
from .enums import Error, ValidationError

_ct_dll = dllLoader.load_dll(win_name='kvaMemoLibXML.dll', linux_name='libkvamemolibxml.so')
dll = KvaMemoLibXmlDll(_ct_dll)


class KvaMemoLibXml:
    """Deprecated wrapper class for the Kvaser kvaMemoLibXml

    .. deprecated:: 1.5

    All functionality of this class has been moved to the kvamemolibxml module itself::

      # deprecated
      from canlib import kvamemolibxml
      cl = kvamemolibxml.KvaMemoLibXml()  # or kvamemolibxml.kvaMemoLibXml()
      cl.functionName()

      # use this instead
      from canlib import kvamemolibxml
      kvamemolibxml.functionName()

    Differences:

    `xmlGetLastError` Does not take any argument, and returns a two-tuple.

    """

    dll = dll

    # These two variables seem to serve no purpose at all, so they will be
    # removed along with KvaMemoLibXml.
    kvaMemoLibXmlDll = dllLoader.load_dll(
        win_name='kvaMemoLibXML.dll', linux_name='libkvamemolibxml.so'
    )
    installDir = os.environ.get('KVDLLPATH')

    def __init__(self):
        deprecation.manual_warn(
            "Creating KvaMemoLibXml objects is deprecated, "
            "all functionality has been moved to the kvamemolib module itself."
        )
        # since=1.5
        self._module = sys.modules[__name__]

    def __getattr__(self, name):
        try:
            return getattr(self._module, name)
        except AttributeError:
            raise AttributeError(
                f"{str(type(self))} object has no attribute {name}"
            )

    @staticmethod
    def xmlGetLastError(kvaERR=0):
        """Get the last error message (if any).

        Get the last error message (if any) from conversion in human redable
        format.

        Args:
            kvaERR (int): kvaMemoLibXml error code.

        Returns:
           msg (`str`): Error message associated with kvaERR.

        """
        msg = ct.create_string_buffer(1 * 1024)
        err = ct.c_int(kvaERR)
        dll.kvaXmlGetLastError(msg, ct.sizeof(msg), ct.byref(err))
        return msg.value


@deprecation.deprecated.favour('dllversion')
def getVersion():
    """Get the kvaMemoLibXml DLL version number as a `str`

    .. deprecated:: 1.5
       Use `dllversion` instead.

    """
    return str(dllversion())


def dllversion():
    """Get the kvaMemoLibXML DLL version number.

    Returns:
        `canlib.VersionNumber`

    """
    v = dll.kvaXmlGetVersion()
    version = VersionNumber(major=v >> 8, minor=v & 0xFF)
    return version


def kvaBufferToXml(conf_lif):
    """Convert a buffer containg param.lif to XML settings.

    Scripts from the param.lif will be written to current working
    directory.

    Args:
        conf_lif (`str`): Buffer containing param.lif to convert.

    Returns:
        `str`: Buffer containing converted XML settings.
    """
    version = ct.c_long(0)
    xml_buf = ct.create_string_buffer(500 * 1024)
    xml_size = ct.c_uint(ct.sizeof(xml_buf))
    script_path = ct.c_char_p(b"")
    dll.kvaBufferToXml(
        ct.c_char_p(conf_lif),
        len(conf_lif),
        xml_buf,
        ct.byref(xml_size),
        ct.byref(version),
        script_path,
    )
    return xml_buf.value.decode('utf8')


def kvaXmlToBuffer(conf_xml):
    """Convert XML settings to param.lif buffer.

    Args:
        conf_xml (`str`): XML settings to convert.

    Returns:
        `str`: Buffer containing converted param.lif.
    """
    version = ct.c_long(0)
    lif_buf = ct.create_string_buffer(320 * 32 * 1024)
    lif_size = ct.c_uint(ct.sizeof(lif_buf))
    c_conf_xml = conf_xml.encode()
    dll.kvaXmlToBuffer(
        c_conf_xml,
        len(c_conf_xml),
        lif_buf,
        ct.byref(lif_size),
        ct.byref(version),
    )
    return lif_buf.raw[: lif_size.value]


def kvaXmlToFile(xml_filename, binary_filename):
    """Convert XML file to binary configuration file.

    Args:
        xml_filename (`str`): Filename of file containing the XML settings.
        binary_filename (`str`): Filename of binary configuration.
    """
    dll.kvaXmlToFile(xml_filename.encode(), binary_filename.encode())


def kvaXmlValidate(conf_xml):
    """Validate a buffer with XML settings.

    Args:
        conf_xml (`str`): string containing the XML settings to validate.

    Returns:
        `tuple`: containing

        - `int`: Number of XML validation errors.
        - `int`: Number of XML validation warnings.
    """
    dll.kvaXmlValidate(conf_xml.encode(), len(conf_xml))
    return xmlGetValidationStatusCount()


def xmlGetValidationStatusCount():
    """Get the number of validation statuses (if any).

    Call after kvaXmlValidate().

    Returns:
        `tuple`: containing

        - `int`: Number of XML validation errors.
        - `int`: Number of XML validation warnings.
    """
    countErr = ct.c_int(0)
    countWarn = ct.c_int(0)
    dll.kvaXmlGetValidationStatusCount(ct.byref(countErr), ct.byref(countWarn))
    return (countErr.value, countWarn.value)


def xmlGetValidationError():
    """Get validation errors (if any).

    Call after kvaXmlValidate() until return status is
    KvaXmlValidationStatusOK.

    Returns:
        `tuple`: containing

        - `int`: Validation error status code.
        - `str`: Validation error status message.

    .. versionchanged:: 1.19
        Returned status code is now an enum.

    """
    status = ct.c_int(-666)
    text = ct.create_string_buffer(1048)
    dll.kvaXmlGetValidationError(ct.byref(status), text, len(text))
    return (ValidationError.from_number(status.value), text.value.decode())


def xmlGetValidationWarning():
    """Get validation warnings (if any).

    Call after kvaXmlValidate() until return status is
    KvaXmlValidationStatusOK.

    Returns:
        `tuple`: containing

        - `int`: Validation warning status code.
        - `str`: Validation warning status message.

    .. versionchanged:: 1.19
        Returned status code is now an enum.

    """
    status = ct.c_int(-666)
    text = ct.create_string_buffer(2048)
    dll.kvaXmlGetValidationWarning(ct.byref(status), text, len(text))
    return (ValidationError.from_number(status.value), text.value.decode())


def xmlGetLastError():
    """Get the last error message (if any).

    Returns:
        `tuple`: containing

        - `str`: Error message associated with the error code.
        - `~.enums.Error`: Error code.

    .. versionchanged:: 1.19
        Returned error code is now an enum.

    """
    msg = ct.create_string_buffer(2 * 1024)
    err = ct.c_int(-666)
    dll.kvaXmlGetLastError(msg, ct.sizeof(msg), ct.byref(err))
    return (msg.value.decode("utf-8"), Error.from_number(err.value))
