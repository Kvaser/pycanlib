# -*- coding: utf-8 -*-

import os
import sys
import time

import pytest

from canlib import canlib, linlib

pytest_plugins = ["envvar_conftest"]

if sys.platform.startswith('win'):
    from canlib import kvrlib
else:
    kvrlib = NotImplemented


winonly = pytest.mark.skipif(
    not sys.platform.startswith('win'),
    reason="only supported on windows",
)

linuxonly = pytest.mark.skipif(
    not sys.platform.startswith('linux'),
    reason="only supported on linux",
)

kvdeprecated = pytest.mark.filterwarnings('ignore::canlib.deprecation.KvDeprecationBase')

collect_ignore = ["setup.py"]
if sys.version_info[0] < 3:
    collect_ignore.append("test_canlib_py3.py")


def is_drivername(name, channel_no):
    chd = canlib.ChannelData(channel_no)
    driver_name = chd.driver_name
    if driver_name.find(name) == -1:
        return False
    else:
        return True


def pytest_addoption(parser):
    parser.addoption(
        "--kvprobe", action="store_true", help="probe for and use available interfaces"
    )


def pytest_report_header(config, start_path):
    if config.getoption('--kvprobe'):
        import kvprobe

        return kvprobe.header()


# Test files that run without the native library (pure-Python logic only). In
# READTHEDOCS mock mode `dllLoader` returns a MagicMock, so every *other* test is
# skipped: anything that calls the library misbehaves against the mock — e.g.
# device.connected_devices() loops forever because the mock never raises. This is
# an explicit allowlist (default-deny) so a new test can never hang the mock run.
_MOCK_SAFE_FILES = frozenset({
    "test_Frame.py",
    "test_ean.py",
    "test_versionnumber.py",
    "test_bound_signal.py",
    "test_kvDevice.py",
})


def pytest_collection_modifyitems(config, items):
    """In READTHEDOCS mock mode, keep only the pure-Python (`_MOCK_SAFE_FILES`) tests."""
    if os.environ.get("READTHEDOCS") != "True":
        return
    skip_mock = pytest.mark.skip(
        reason="needs the native library; skipped in READTHEDOCS mock mode"
    )
    for item in items:
        if os.path.basename(str(item.fspath)) not in _MOCK_SAFE_FILES:
            item.add_marker(skip_mock)


@pytest.fixture
def datadir():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    return path


@pytest.fixture
def kvaser_driver():
    """Skip when the Kvaser driver is not installed.

    Some `@winonly` kvrlib tests round-trip the driver-backed "info set" storage,
    which needs no hardware but does need the driver. The driver also provides the
    virtual CAN channels, so a channel count of zero is a reliable "no driver"
    signal (`getNumberOfChannels` counts virtual channels).
    """
    if canlib.getNumberOfChannels() == 0:
        pytest.skip("requires the Kvaser driver (no CAN channels available)")


@pytest.fixture(scope="session")
def kvprobe(request):
    if request.config.getoption('--kvprobe'):
        import kvprobe

        return kvprobe
    else:
        pytest.skip()


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "feature('script'): skip test if feature doesn't exist on channel(s)",
    )


@pytest.fixture
def channel_no(request, kvprobe):
    marker = 'feature'
    if request.node.get_closest_marker(marker):
        feat = request.node.get_closest_marker(marker).args[0]

        if feat:
            return feat[0]
        else:
            pytest.skip()
    else:
        try:
            return kvprobe.can[0]
        except IndexError:
            pytest.skip()


@pytest.fixture
def channel_no_pair(request, kvprobe):
    marker = 'feature'
    if request.node.get_closest_marker(marker):
        feat = request.node.get_closest_marker(marker).args[0]

        if feat and len(feat) > 1:
            return feat
        else:
            pytest.skip()
    else:
        try:
            return kvprobe.can[:2]
        except IndexError:
            pytest.skip()


@pytest.fixture
def chA(channel_no_pair):
    with canlib.openChannel(
        channel_no_pair[0],
        flags=canlib.Open.ACCEPT_VIRTUAL | canlib.Open.REQUIRE_INIT_ACCESS,
    ) as chA:
        chA.setBusParams(canlib.canBITRATE_500K)
        yield chA


@pytest.fixture
def chB(channel_no_pair):
    with canlib.openChannel(
        channel_no_pair[1],
        flags=canlib.Open.ACCEPT_VIRTUAL | canlib.Open.REQUIRE_INIT_ACCESS,
    ) as chB:
        chB.setBusParams(canlib.canBITRATE_500K)
        yield chB


@pytest.fixture(scope="session")
def remote_no(kvprobe):
    try:
        return kvprobe.remote[0]
    except IndexError:
        pytest.skip()


@pytest.fixture(scope="session")
def local_r_no(kvprobe):
    try:
        return kvprobe.local_r[0]
    except IndexError:
        pytest.skip()


@pytest.fixture
def rdev(remote_no):
    return kvrlib.openDevice(remote_no)


@pytest.fixture
def ldev(local_r_no):
    return kvrlib.openDevice(local_r_no)


@pytest.fixture(scope="session")
def lin_no(kvprobe):
    try:
        return kvprobe.lin[0]
    except IndexError:
        pytest.skip()


@pytest.fixture(scope="session")
def lin_no_pair(kvprobe):
    try:
        return (kvprobe.lin[0], kvprobe.lin[1])
    except IndexError:
        pytest.skip()


@pytest.fixture
def master(lin_no_pair):
    """Fixture for a LIN channel opened as a master"""
    with linlib.openMaster(lin_no_pair[0], bps=2 * 10 ** 4) as master:
        yield master

@pytest.fixture
def slave(lin_no_pair):
    """Fixture for a LIN channel opened as a slave"""
    with linlib.openSlave(lin_no_pair[1], bps=2 * 10 ** 4) as slave:
        yield slave


@pytest.fixture(scope="session")
def iopin_no(kvprobe):
    try:
        return kvprobe.iopin[0]
    except IndexError:
        pytest.skip()


@pytest.fixture(scope="session")
def script_no(kvprobe):
    try:
        return kvprobe.script[0]
    except IndexError:
        pytest.skip()


@pytest.fixture(scope="session")
def script_no_pair(kvprobe):
    try:
        return (kvprobe.script[0], kvprobe.script[1])
    except IndexError:
        pytest.skip()


# # You may apply a filter to all tests of a class by using the filterwarnings
# # mark as a class decorator or to all tests in a module by setting the
# # pytestmark variable:
# pytestmark = pytest.mark.filterwarnings('error')

def wait_until(predicate, timeout, period=0.1, *args, **kwargs):
    end = time.time() + timeout
    while time.time() < end:
        if predicate(*args, **kwargs):
            return True
        time.sleep(period)
    return False
