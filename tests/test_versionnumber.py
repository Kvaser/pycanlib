import pytest

from canlib import BetaVersionNumber, VersionNumber


def test_VersionNumber():
    v12 = VersionNumber(1, 2)
    assert v12 == VersionNumber(1, 2)
    assert str(v12)
    assert v12 < VersionNumber(2)
    assert v12 > VersionNumber(1, 1)

    assert v12 == (1, 2)
    assert v12 < (2,)
    assert v12 > (1, 1)

    assert v12.major == 1
    assert v12.minor == 2
    assert v12.release is None
    assert v12.build is None

    assert repr(v12) != str(v12)


@pytest.mark.parametrize("v_class", [VersionNumber, BetaVersionNumber])
def test_VersionNumber_init(v_class):
    vp = v_class(1)
    vk = v_class(major=1)
    print(vp)
    print(vk)
    assert vp == vk

    vp = v_class(1, 2)
    vk = v_class(major=1, minor=2)
    print(vp)
    print(vk)
    assert vp == vk

    vp = v_class(1, 2, 3)
    vk = v_class(major=1, minor=2, build=3)
    print(vp)
    print(vk)
    assert vp == vk

    vp = v_class(1, 2, 4, release=3)
    vk = v_class(major=1, minor=2, release=3, build=4)
    print(vp)
    print(vk)
    assert vp == vk

    invalid_kwargs = (
        {'minor': 1},
        {'release': 1},
        {'build': 1},
        {'minor': 1, 'release': 2},
        {'minor': 1, 'build': 2},
        {'release': 1, 'build': 2},
        {'minor': 1, 'release': 2, 'build': 3},
        {'major': 1, 'release': 2},
        {'major': 1, 'build': 2},
        {'major': 1, 'release': 2, 'build': 3},
        {'major': 1, 'minor': 2, 'release': 3},
    )
    for kwargs in invalid_kwargs:
        with pytest.raises(TypeError):
            print(v_class(**kwargs), f'({kwargs})')

    # python 2 does not support keyword-only arguments
    with pytest.raises(TypeError):
        print(v_class(1, 2, 3, 4, 5, 6, 7), '((1, 2, 3, 4, 5, 6, 7))')


def test_BetaVersionNumber_init():
    vp = VersionNumber(1, 2)
    vk = BetaVersionNumber(major=1, minor=2)
    print(vp)
    print(vk)
    assert vp != vk
    assert vk != vp
    assert vp == (1, 2)
    assert vk != (1, 2)
    vp = BetaVersionNumber(1, 2, 4, 3)
    vk = BetaVersionNumber(major=1, minor=2, release=3, build=4)
    print(vp)
    print(vk)
    print(repr(vk))
    assert vp == vk
