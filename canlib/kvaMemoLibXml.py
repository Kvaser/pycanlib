import sys
import warnings

from . import kvamemolibxml

warnings.warn(
    DeprecationWarning(
        "Using canlib.kvaMemoLibXml is deprecated, please use canlib.kvamemolibxml instead"
    )
)

sys.modules[__name__] = kvamemolibxml
