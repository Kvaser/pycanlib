# 1. Download and start test_envvar.t
# 1b. Read CAN messages with init values, verify correct values
# 2. Setenv IntVal with random value
# 3. Check can message id=121 contain same value
#
# 4. Send CAN message id=131 with random value
# 5. Check Getenv IntVal have same value
#
# - Check float envvar
# - Check char[] whole and parts
# - Check envvar event

import math
import struct

import pytest

from canlib import Frame

INT_VALUES = [15, 0, -255, 256, -1, 2147483647, -2147483648]
FLOAT_VALUES = [
    math.pi,
    -math.pi,
    0,
    math.e,
    -math.e,
    1.2 * math.pow(10, -38),
    3.4 * math.pow(10, 38),
    -1.3333,
]


@pytest.mark.parametrize('value', INT_VALUES)
def test_write_IntVal(envvar_t, pycan_ch, value):
    envvar_t.envvar.IntVal = value
    frame = pycan_ch.read(timeout=5000)
    assert frame.id == 121
    # read_data = int.from_bytes(frame.data, byteorder='big', signed=True)
    read_data = struct.unpack(">i", frame.data)[0]
    assert read_data == value


@pytest.mark.parametrize('value', INT_VALUES)
def test_read_IntVal(envvar_t, pycan_ch, value):
    # Not available in python 2.7
    # data = value.to_bytes(4, byteorder='big', signed=True)
    data = struct.pack(">i", value)
    frame = Frame(id_=131, data=data)
    print("Sending:", frame)
    pycan_ch.write(frame)

    # We will get a CAN message when envvar is set, let us read this now and
    # meanwhile will the envvar have time to propagate...
    frame = pycan_ch.read(timeout=5000)
    print("Reading:", frame)
    assert frame.id == 121

    # read_data = int.from_bytes(frame.data, byteorder='big', signed=True)
    read_data = struct.unpack(">i", frame.data)[0]
    assert read_data == value

    # Check expected value
    assert value == envvar_t.envvar.IntVal


@pytest.mark.parametrize('value', FLOAT_VALUES)
def test_write_FloatVal(envvar_t, pycan_ch, value):
    envvar_t.envvar.FloatVal = value
    frame = pycan_ch.read(timeout=5000)
    print("Reading:", frame)
    assert frame.id == 122
    data_array = struct.unpack('>f', frame.data)
    assert data_array[0] == pytest.approx(value)


@pytest.mark.parametrize('value', FLOAT_VALUES)
def test_read_FloatVal(envvar_t, pycan_ch, value):
    # Adjust value to be a perfect match in a 4 byte float
    value = struct.unpack('>f', struct.pack('>f', value))[0]

    data = struct.pack('>f', value)
    frame = Frame(id_=132, data=data)
    print("Sending:", frame)
    pycan_ch.write(frame)

    # We will get a CAN message when envvar is set, let us read this now and
    # meanwhile will the envvar have time to propagate...
    frame = pycan_ch.read(timeout=5000)
    print("Reading:", frame)
    assert frame.id == 122
    data_array = struct.unpack('>f', frame.data)
    assert data_array[0] == value

    # Check expected value
    assert value == envvar_t.envvar.FloatVal
