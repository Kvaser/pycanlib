# Version comes from the installed package metadata (static `version` in
# pyproject.toml — the single source of truth).
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("canlib")
except PackageNotFoundError:
    # Source checkout that was never installed.
    __version__ = "0.0.0+unknown"

from .device import Device, connected_devices
from .ean import EAN
from .exceptions import CanlibException, DllException
from .frame import Frame, LINFrame
from .versionnumber import BetaVersionNumber, VersionNumber
