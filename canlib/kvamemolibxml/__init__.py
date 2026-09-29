"""Wrapper for the Kvaser kvaMemoLibXml library

The kvaMemoLibXML is a library for converting XML settings to a binary
param.lif for Kvaser Memorator 2nd Generation

The binary settings used by Kvaser Memorator 2nd Generation are extensive and
an API that covers all possibilities would be very complex. A better approach
is to use XML to describe the settings and parse them into a binary settings
file with an external library.

The XML conversion results in a binary settings file, param.lif, that can be
downloaded to a Kvaser Memorator 2nd Generation with the KvmLib API call
``kvmKmfWriteConfig()``.

"""

from .configuration import (Configuration, ValidationErrorMessage,
                            ValidationMessage, ValidationWarningMessage,
                            load_lif, load_lif_file, load_xml, load_xml_file)
from .constants import *
from .enums import Error, ValidationError, ValidationWarning
from .exceptions import KvaError  # for backwards-compatibility
from .exceptions import KvaError as kvaError
from .wrapper import KvaMemoLibXml  # for backwards-compatibility
from .wrapper import KvaMemoLibXml as kvaMemoLibXml
from .wrapper import (dllversion, getVersion, kvaBufferToXml, kvaXmlToBuffer,
                      kvaXmlToFile, kvaXmlValidate, xmlGetLastError,
                      xmlGetValidationError, xmlGetValidationStatusCount,
                      xmlGetValidationWarning)
