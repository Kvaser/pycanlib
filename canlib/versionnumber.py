class VersionNumber(tuple):
    """A tuple-subclass representing a version number

    Version numbers can be created using one to three positional arguments,
    representing the major, minor, and build number respectively::

        v1 = VersionNumber(1)
        v12 = VersionNumber(1, 2)
        v123 = VersionNumber(1, 2, 3)

    Keyword arguments can also be used::

        v1 = VersionNumber(major=1)
        v12 = VersionNumber(major=1, minor=2)
        v123 = VersionNumber(major=1, minor=2, build=3)

    A fourth number, the release number, can also be given as a keyword-only
    argument::

        v1293 = VersionNumber(major=1, minor=2, release=9, build=3)

    This release number is placed between the minor and build numbers, both for
    the string representation and in the tuple.

    The major number is required and the other numbers are optional in the
    order minor, build, release.

    All numbers can be accessed as attributes (`major`, `minor`, `release`,
    `build`). If the number is unavailable, accessing the attribute returns
    `None`.

    """

    __slots__ = ()

    def __new__(cls, major, minor=None, build=None, release=None):
        # qqqdaca python 2 :: in python 3, release should be keyword-only argument

        if __debug__:
            try:
                if release is not None:
                    assert build is not None
                if build is not None:
                    assert minor is not None
                if minor is not None:
                    assert major is not None
            except AssertionError:
                raise TypeError(
                    "VersionNumber members are optional in the following order: "
                    "[major [minor [[release] build]"
                )

        numbers = (n for n in (major, minor, release, build) if n is not None)
        obj = super().__new__(cls, numbers)
        return obj

    def __str__(self):
        return '.'.join(str(n) for n in self)

    def __repr__(self):
        attrs = (
            f'{name}={getattr(self, name)}'
            for name in ('major', 'minor', 'release', 'build')
        )
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    @property
    def major(self):
        try:
            return self[0]
        except IndexError:
            return None

    @property
    def minor(self):
        try:
            return self[1]
        except IndexError:
            return None

    @property
    def release(self):
        if len(self) > 3:
            return self[2]
        else:
            return None

    @property
    def build(self):
        if len(self) > 2:
            return self[-1]
        else:
            return None

    @property
    def beta(self):
        return False


class BetaVersionNumber(VersionNumber):
    """A tuple-subclass representing a beta (preview) version number

    A `VersionNumber` that also has the attribute `beta` set to true.

    .. versionadded:: 1.6

    """

    def __eq__(self, other):
        if not isinstance(other, BetaVersionNumber):
            return False
        return super().__eq__(other) and self.beta == other.beta

    # For Python 2
    def __ne__(self, other):
        return not self == other

    def __str__(self):
        txt = super().__str__() + ' Beta'
        return txt

    @property
    def beta(self):
        return True
