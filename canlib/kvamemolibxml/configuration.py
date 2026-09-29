from collections import namedtuple

from .enums import ValidationError, ValidationWarning
from .wrapper import (kvaBufferToXml, kvaXmlToBuffer, kvaXmlValidate,
                      xmlGetValidationError, xmlGetValidationWarning)


def load_lif(lif_bytes):
    """Create a `Configuration` from a param.lif `bytes`

    Args:
        lif_bytes (`bytes`): Binary configuration in param.lif format

    """
    return Configuration(lif=lif_bytes)


def load_lif_file(filepath):
    """Like `load_lif` but takes a path to a file containing the lif configuration"""
    with open(filepath, 'rb') as f:
        lif_bytes = f.read()
    return load_lif(lif_bytes)


def load_xml(xml_string):
    """Create a `Configuration` from an xml `string`

    Args:
        xml_string (`str`): XML configuration

    """
    return Configuration(xml=xml_string)


def load_xml_file(filepath):
    """Like `load_lif` but takes a path to a file containing the XML configuration"""
    with open(filepath) as f:
        xml_string = f.read()
    return load_xml(xml_string)


ValidationResult = namedtuple('ValidationResult', "errors, warnings")
"""Validation errors and warnings.

    Args:
        errors (list(`int`)): Valdiation errors.
        warnings ([`str`]): Validation warnings.

"""

ValidationMessage = namedtuple('ValidationMessage', "code text")
"""Validation code and message.

    Args:
        code (`int`): Valdiation status code.
        text (`str`): Validation message.

"""


class ValidationErrorMessage(ValidationMessage):
    """An error found during validation"""

    __slots__ = ()

    def __str__(self):
        return f"Error: {self.text} ({self.code!s})"


class ValidationWarningMessage(ValidationMessage):
    """A warning found during validation"""

    __slots__ = ()

    def __str__(self):
        return f"Warning: {self.text} ({self.code!s})"


class Configuration:
    """Configuration data for Kvaser devices

    It is usually preferred to create objects of this class with one of the
    functions:

    * `load_xml`
    * `load_xml_file`
    * `load_lif`
    * `load_lif_file`

    The XML and param.lif representation of this configuration can be accessed
    with the `xml` and `lif` attributes, respectively.

    Two `Configuration` objects can be tested for equality::

        config1 == config2

    This will test whether the objects are equivalent: whether they have the
    same param.lif representation.

    Finally, the configuration can be validated with `Configuration.validate`::

        errors, warnings = configuration.validate()
        for error in errors:
            print(error)
        for warning in warnings:
            print(warning)
        if errors:
            raise ValueError("Invalid configuration")

    .. versionadded: 1.6

    """

    def __init__(self, xml=None, lif=None):
        if xml is None and lif is None:
            raise TypeError("Either xml or lif required")
        self._xml = xml
        self._lif = lif

    def __eq__(self, other):
        # Two xml strings might be formatted differently while still
        # equivalent, so we need to compare the binary lif
        return self.lif == other.lif

    @property
    def xml(self):
        """`str`: The XML representation of this configuration"""
        if self._xml is None:
            self._xml = kvaBufferToXml(self._lif)
        return self._xml

    @property
    def lif(self):
        """`bytes`: The param.lif representation of this configuration"""
        if self._lif is None:
            self._lif = kvaXmlToBuffer(self._xml)
        return self._lif

    def validate(self):
        """Validate this configuration

        Validates the XML representation of this configuration, and returns a
        tuple ``(errors, warnings)`` where ``errors`` is a `list` of
        `~canlib.kvamemolibxml.ValidationError` and ``warnings`` is a `list`
        `~canlib.kvamemolibxml.ValidationWarning`.

        """
        kvaXmlValidate(self.xml)
        errors = list(self._errors())
        warnings = list(self._warnings())
        return ValidationResult(errors, warnings)

    def _warnings(self):
        while True:
            code, text = xmlGetValidationWarning()
            if code != 0:
                yield ValidationWarningMessage(ValidationWarning(code), text.rstrip())
            else:
                return

    def _errors(self):
        while True:
            code, text = xmlGetValidationError()
            if code != 0:
                yield ValidationErrorMessage(ValidationError(code), text.rstrip())
            else:
                return
