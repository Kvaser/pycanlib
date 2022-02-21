# -*- coding: utf-8 -*-

import pytest
from conftest import winonly

from canlib import Frame, canlib


def collect_on_hook_DataVal_response(ch):

    msg = bytearray()
    while True:
        frame = ch.read(timeout=500)
        if frame.id == 125:
            break
        if frame.id == 124:
            msg.extend(frame.data)
    return msg


def send_DataVal_on_can(ch, data):
    chunk_size = 8
    frame = Frame(id_=133, data=[0, 0, 0, 0, 0, 0, 16, 0])
    ch.write(frame)
    for i in range(0, len(data), chunk_size):
        frame = Frame(id_=134, data=data[i:i + chunk_size])
        ch.writeWait(frame, timeout=500)
    frame = Frame(id_=135, data=[])
    ch.writeWait(frame, timeout=500)


@winonly
def test_scriptEnvvarGetData_deprecation(envvar_t):
    with canlib.openChannel(envvar_t.channel_number) as ch:
        ehnd, etype, esize = ch.scriptEnvvarOpen('DataVal')
        with pytest.deprecated_call():
            ch.scriptEnvvarGetData(ehnd, esize)
        ch.scriptEnvvarClose(ehnd)


@winonly
def test_scriptEnvvarSetData_deprecation(envvar_t, pycan_ch, char_text_1):
    with canlib.openChannel(envvar_t.channel_number) as ch:
        ehnd, etype, esize = ch.scriptEnvvarOpen('DataVal')
        value = char_text_1
        with pytest.deprecated_call():
            ch.scriptEnvvarSetData(ehnd, value, esize)
        _ = collect_on_hook_DataVal_response(pycan_ch)
        # envvar_t.ch.iocontrol.flush_rx_buffer()
        # pycan_ch.iocontrol.flush_tx_buffer()
        ch.scriptEnvvarClose(ehnd)


@winonly
def test_write_full_byte_envvar(envvar_t, pycan_ch, char_text_1):
    data = bytearray(char_text_1.encode('utf-8'))
    envvar_t.envvar.DataVal = data
    msg = collect_on_hook_DataVal_response(pycan_ch)
    assert data == msg


@winonly
def test_read_full_byte_envvar(envvar_t, pycan_ch, char_text_1):
    data = bytearray(char_text_1.encode('utf-8'))
    assert type(data) == bytearray
    send_DataVal_on_can(pycan_ch, data)
    msg = collect_on_hook_DataVal_response(pycan_ch)
    value = envvar_t.envvar.DataVal
    assert data == msg
    assert data == value


@winonly
def test_write_full_byte_padded_envvar(envvar_t, pycan_ch, char_text_1):
    # We need to pad a shorter bytearray in order to write full entry
    size = len(envvar_t.envvar.DataVal)
    data = 'Hej på dig'.encode('utf-8').ljust(size, b'\0')
    envvar_t.envvar.DataVal = data
    msg = collect_on_hook_DataVal_response(pycan_ch)
    assert len(msg) == len(data)
    assert msg == data


@winonly
def test_read_full_byte_padded_envvar(envvar_t, pycan_ch, char_text_1):
    size = len(envvar_t.envvar.DataVal)
    data = 'Hej på dig'.encode('utf-8').ljust(size, b'\0')
    assert type(data) == bytes
    send_DataVal_on_can(pycan_ch, data)
    msg = collect_on_hook_DataVal_response(pycan_ch)
    value = envvar_t.envvar.DataVal
    assert len(data) == len(value)
    assert data == msg
    assert data == value


@winonly
def test_write_full_byte_script_padded_envvar(envvar_t, pycan_ch, char_text_1):
    # The padding is included in the ScriptRunner
    data = envvar_t.pad("Hej från mig".encode('utf-8'), 'DataVal')
    envvar_t.envvar.DataVal = data
    msg = collect_on_hook_DataVal_response(pycan_ch)
    assert msg == data


@winonly
def test_write_full_array_envvar(envvar_t, pycan_ch, char_text_1):
    # Using an array
    size = len(envvar_t.envvar.DataVal)
    data = [5] * size
    data[2] = 2
    data[4] = 4
    envvar_t.envvar.DataVal = data
    msg = collect_on_hook_DataVal_response(pycan_ch)
    assert msg == bytearray(data)
    assert list(msg) == data


@winonly
def test_write_read_full_array_envvar(envvar_t, pycan_ch, char_text_1):
    # Using an array
    size = len(envvar_t.envvar.DataVal)
    data = [5] * size
    data[2] = 2
    data[4] = 4
    data = envvar_t.envvar.DataVal = data
    msg = collect_on_hook_DataVal_response(pycan_ch)
    read = envvar_t.envvar.DataVal
    assert msg == bytearray(data)
    assert list(read) == data


@winonly
def test_write_full_string_envvar(envvar_t, pycan_ch, char_text_1):
    data = char_text_1.encode('utf-8')
    envvar_t.envvar.DataVal = data
    msg = collect_on_hook_DataVal_response(pycan_ch)
    assert char_text_1 == msg.decode('utf-8')


@winonly
def test_read_full_string_envvar(envvar_t, pycan_ch, char_text_1):
    data = char_text_1.encode('utf-8')
    send_DataVal_on_can(pycan_ch, data)
    msg = collect_on_hook_DataVal_response(pycan_ch)
    value = envvar_t.envvar.DataVal
    assert data == msg
    assert char_text_1 == str(value)


@winonly
def test_write_full_bytearray_envvar(envvar_t, pycan_ch, char_text_1):
    # Using an array
    size = len(envvar_t.envvar.DataVal)
    data = [5] * size
    data[2] = 2
    data[4] = 4
    data = envvar_t.envvar.DataVal = bytearray(data)
    msg = collect_on_hook_DataVal_response(pycan_ch)
    assert msg == data


@winonly
def test_read_full_array_envvar(envvar_t, pycan_ch, char_text_1):
    size = len(envvar_t.envvar.DataVal)
    data = [5] * size
    data[2] = 2
    data[4] = 4
    send_DataVal_on_can(pycan_ch, data)
    msg = collect_on_hook_DataVal_response(pycan_ch)
    value = envvar_t.envvar.DataVal
    assert len(data) == len(value)
    assert bytes(data) == msg
    assert bytes(data) == value


@winonly
def test_invalid_slicing_envvar(envvar_t):
    ival = envvar_t.envvar.IntVal
    with pytest.raises(TypeError):
        print('IVAL:', ival[2:3])
    with pytest.raises(TypeError):
        ival[5] = 7


@winonly
def test_write_partial_char_single_byte_envvar(envvar_t, pycan_ch, char_text_1, char_text_2):
    size = len(envvar_t.envvar.DataVal)
    len_char_text_1 = len(char_text_1)
    assert size == len_char_text_1

    envvar_t.envvar.DataVal = char_text_1.encode('utf-8')
    msg = collect_on_hook_DataVal_response(pycan_ch)
    expected_text = char_text_1
    expected_text = expected_text[:495] + char_text_2[495] + expected_text[496:]
    envvar_t.envvar.DataVal[495] = char_text_2[495].encode('utf-8')
    msg = collect_on_hook_DataVal_response(pycan_ch)
    text = envvar_t.envvar.DataVal
    assert msg == text
    assert len(expected_text) == len(text)
    assert expected_text == str(text)


@winonly
def test_write_partial_char_start_slice_envvar(envvar_t, pycan_ch, char_text_1, char_text_2):
    size = len(envvar_t.envvar.DataVal)
    len_char_text_1 = len(char_text_1)
    assert size == len_char_text_1

    envvar_t.envvar.DataVal = char_text_1.encode('utf-8')
    msg = collect_on_hook_DataVal_response(pycan_ch)
    expected_text = char_text_1
    expected_text = char_text_2[:100] + expected_text[100:]
    envvar_t.envvar.DataVal[:100] = char_text_2[:100].encode('utf-8')
    msg = collect_on_hook_DataVal_response(pycan_ch)
    text = envvar_t.envvar.DataVal
    assert msg == text
    assert len(expected_text) == len(text)
    assert expected_text == str(text)


@winonly
def test_write_partial_char_middle_slice_envvar(envvar_t, pycan_ch, char_text_1, char_text_2):
    size = len(envvar_t.envvar.DataVal)
    len_char_text_1 = len(char_text_1)
    assert size == len_char_text_1

    envvar_t.envvar.DataVal = char_text_1.encode('utf-8')
    msg = collect_on_hook_DataVal_response(pycan_ch)
    expected_text = char_text_1[:15] + char_text_2[15:200] + char_text_1[200:]
    envvar_t.envvar.DataVal[15:200] = char_text_2.encode('utf-8')[15:200]
    msg = collect_on_hook_DataVal_response(pycan_ch)
    text = envvar_t.envvar.DataVal
    assert msg == text
    assert len(expected_text) == len(text)
    assert expected_text == str(text)


@winonly
def test_write_partial_char_stop_slice_envvar(envvar_t, pycan_ch, char_text_1, char_text_2):
    size = len(envvar_t.envvar.DataVal)
    len_char_text_1 = len(char_text_1)
    assert size == len_char_text_1

    envvar_t.envvar.DataVal = char_text_1.encode('utf-8')
    msg = collect_on_hook_DataVal_response(pycan_ch)
    expected_text = char_text_1[:4000] + char_text_2[4000:]
    envvar_t.envvar.DataVal[4000:] = char_text_2.encode('utf-8')[4000:]
    msg = collect_on_hook_DataVal_response(pycan_ch)
    text = envvar_t.envvar.DataVal
    assert msg == text
    assert text == msg
    assert len(expected_text) == len(text)
    assert expected_text == str(text)


@winonly
def test_read_partial_char_single_byte_envvar(envvar_t, pycan_ch, char_text_1, char_text_2):
    envvar_t.envvar.DataVal = char_text_1.encode('utf-8')
    _ = collect_on_hook_DataVal_response(pycan_ch)

    expected_text = char_text_1
    expected_text = expected_text[:495] + char_text_2[495] + expected_text[496:]
    send_DataVal_on_can(pycan_ch, expected_text.encode('utf-8'))
    _ = collect_on_hook_DataVal_response(pycan_ch)
    text = envvar_t.envvar.DataVal[495]
    assert expected_text[495] == chr(text)


@winonly
def test_read_partial_char_start_slice_envvar(envvar_t, pycan_ch, char_text_1, char_text_2):
    envvar_t.envvar.DataVal = char_text_1.encode('utf-8')
    _ = collect_on_hook_DataVal_response(pycan_ch)

    expected_text = char_text_1
    send_DataVal_on_can(pycan_ch, expected_text.encode('utf-8'))
    _ = collect_on_hook_DataVal_response(pycan_ch)
    text = envvar_t.envvar.DataVal[100:]
    assert len(text) == len(expected_text[100:])
    assert text == expected_text[100:].encode('utf-8')


@winonly
def test_read_partial_char_middle_slice_envvar(envvar_t, pycan_ch, char_text_1, char_text_2):
    envvar_t.envvar.DataVal = char_text_1.encode('utf-8')
    _ = collect_on_hook_DataVal_response(pycan_ch)

    expected_text = char_text_1[:15] + char_text_2[15:200] + char_text_1[200:]
    send_DataVal_on_can(pycan_ch, expected_text.encode('utf-8'))
    _ = collect_on_hook_DataVal_response(pycan_ch)
    text = envvar_t.envvar.DataVal[15:200]
    assert len(text) == len(expected_text[15:200])
    assert text == expected_text[15:200].encode('utf-8')


@winonly
def test_read_partial_char_stop_slice_envvar(envvar_t, pycan_ch, char_text_1, char_text_2):
    envvar_t.envvar.DataVal = char_text_1.encode('utf-8')
    _ = collect_on_hook_DataVal_response(pycan_ch)

    expected_text = char_text_1[:4000] + char_text_2[4000:]
    send_DataVal_on_can(pycan_ch, expected_text.encode('utf-8'))
    _ = collect_on_hook_DataVal_response(pycan_ch)
    text = envvar_t.envvar.DataVal[:4000]
    assert len(text) == len(expected_text[:4000])
    assert text == expected_text[:4000].encode('utf-8')
