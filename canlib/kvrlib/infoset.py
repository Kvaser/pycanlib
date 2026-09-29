# Python 2 does not have abc module
try:
    from collections.abc import MutableSet
except ImportError:
    from collections import MutableSet

from .. import EAN, CanlibException
from .discovery import (DeviceInfo, start_discovery, store_devices,
                        stored_devices)


def discover_info_set(delay=100, timeout=1000, addresses=None, report_stored=True):
    with start_discovery(delay, timeout, addresses, report_stored) as disc:
        info_set = DeviceInfoSet(disc.results())
    return info_set


def empty_info_set():
    return DeviceInfoSet()


def stored_info_set():
    return DeviceInfoSet(stored_devices())


class DeviceNotInSetError(KeyError, CanlibException):
    pass


class DeviceInfoSet(MutableSet):
    """A mutable set of `DeviceInfo` objects that can be written to the registry

    There are three different functions for creating `DeviceInfoSet` objects:

    - `empty_info_set`: Creates an empty set.

    - `stored_info_set`: Creates a set from the device information stored in the registry.

    - `discover_info_set`: Create a set from the results of a `Discovery`.

    Once a `DeviceInfoSet` has been created it can be modified as a normal set,
    and the `DeviceInfo` elements can also be modified. Once all modification
    is done, the set can be written to the registry with `DeviceInfoSet.store`.

    The main difference between `DeviceInfoSet` and normal sets is that it can
    only contain one `DeviceInfo` with a specific combination of EAN and serial
    number, even if they otherwise are not equal. This means that even if
    ``info in infoset`` evaluates to true, that exact object may not be in the
    set, and modifying it may not change the set.

    To retrieve a specific `DeviceInfo` from the set use `DeviceInfoSet.find`::

        info = infoset.find(ean='01234-5', serial=42)

    Modifying the resulting `DeviceInfo` will then change the contents of the set.

    Instances of this class can also be used as context managers, in which case
    they will write their content to the registry when the context exists.

    """

    @staticmethod
    def _elemid(el):
        return (el.ean, el.serial)

    def __init__(self, iterable=None):
        self._elements = dict()
        if iterable is not None:
            self.update(iterable)

    def __contains__(self, el):
        if not isinstance(el, DeviceInfo):
            return False

        elemid = self._elemid(el)
        return elemid in self._elements

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.store()

    def __iter__(self):
        return iter(self._elements.values())

    def __len__(self):
        return len(self._elements)

    def add(self, info):
        """Add a `DeviceInfo` to this `DeviceInfoSet`

        Args:
            info (`DeviceInfo`): The element to add to this set

        If the set already contains a `DeviceInfo` with the same EAN and serial
        number as ``info``, the previous `DeviceInfo` will be discarded and
        replaced by ``info``.

        """
        if not isinstance(info, DeviceInfo):
            raise TypeError(
                "{cls} objects can only contain DeviceInfo objects".format(
                    cls=self.__class__.__name__
                )
            )
        self._elements[self._elemid(info)] = info

    def discard(self, info):
        elemid = self._elemid(info)
        if elemid in self._elements:
            del self._elements[elemid]

    def find(self, ean, serial):
        """Find and return a specific `DeviceInfo` in this set

        Args:
            ean (`~canlib.ean.EAN`): The EAN to search for
            serial (`int`): The serial number to search for

        If no `DeviceInfo` with the EAN and serial number is found in this set,
        `DeviceNotInSetError` is raised.

        Note that there can never be more than one `DeviceInfo` with the same
        EAN and serial number in a `DeviceInfoSet`.

        """
        elemid = (EAN(ean), serial)
        if elemid in self._elements:
            return self._elements[elemid]
        else:
            raise DeviceNotInSetError(
                f"No device info matching ean={ean} and serial={serial} found"
            )

    def find_remove(self, ean, serial):
        """Find a specific `DeviceInfo` and remove it from this set

        Like `DeviceInfoSet.find` but immediately removes the `DeviceInfo` found from the set.

        Args:
            ean (`~canlib.ean.EAN`): The EAN to search for
            serial (`int`): The serial number to search for

        """
        self.remove(self.find(ean, serial))

    def has(self, ean, serial):
        """Check whether the set contains a specific `DeviceInfo`

        Similar to `DeviceInfoSet.find` but instead of returning a `DeviceInfo`
        or raising an exception, this function returns `True` or `False`.

        Args:
            ean (`~canlib.ean.EAN`): The EAN to search for
            serial (`int`): The serial number to search for

        """
        return (EAN(ean), serial) in self._elements

    def new_info(self, ean, serial, **attrs):
        """Create and return new `DeviceInfo` in this set

        Any attribute of the `DeviceInfo` that should have a specific value can
        be passed as keyword arguments to this function.

        The EAN and serial number must be provided.

        Args:
            ean (`~canlib.ean.EAN`): The EAN of the info (`DeviceInfo.ean`)
            serial (`int`): The serial number of the info (`DeviceInfo.serial`)
            attrs: Any other attributes to be set on the `DeviceInfo`

        If the set already contains a `DeviceInfo` with the EAN ``ean`` and
        serial number ``serial``, the previous `DeviceInfo` will be discarded
        and replaced by the new `DeviceInfo` created by this function.

        """
        info = DeviceInfo()
        info.ean = ean
        info.serial = serial
        info.update(attrs)
        self.add(info)
        return info

    def store(self):
        """Store this set's `DeviceInfo` objects in the registry"""
        store_devices(self)

    def update(self, *others):
        """Update the set, adding elements from all others

        All ``others`` must contain nothing but `DeviceInfo` objects, or this
        function will raise `TypeError` without modifying this `DeviceInfoSet`.

        """
        infos = tuple(info for iterable in others for info in iterable)
        if not all(isinstance(info, DeviceInfo) for info in infos):
            raise TypeError(
                "{cls} objects can only contain DeviceInfo objects".format(
                    cls=self.__class__.__name__
                )
            )

        for info in infos:
            self.add(info)
