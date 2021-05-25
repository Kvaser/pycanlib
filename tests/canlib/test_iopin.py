import pytest
from kvprobe import features

from canlib import canlib
from canlib.canlib import iopin


def test_unconfirmed(iopin_no):
    # A newly opened channel is unconfirmed
    with canlib.openChannel(iopin_no) as iopin_ch:
        examined_classes = []
        for pin in iopin_ch.io_pins():
            if type(pin).__name__ in examined_classes:
                continue

            examined_classes.append(type(pin).__name__)
            print(pin)
            if pin.pin_type == iopin.PinType.ANALOG and pin.direction == iopin.Direction.IN:
                value = 6
                if pin.module_type != iopin.ModuleType.INTERNAL:
                    pin.hysteresis = value
                    pin.lp_filter_order = value
                with pytest.raises(canlib.IoPinConfigurationNotConfirmed):
                    value = pin.value

            elif pin.pin_type == iopin.PinType.DIGITAL and pin.direction == iopin.Direction.IN:
                value = 6
                if pin.module_type != iopin.ModuleType.INTERNAL:
                    pin.high_low_filter = value
                    pin.low_high_filter = value
                with pytest.raises(canlib.IoPinConfigurationNotConfirmed):
                    value = pin.value
            elif pin.pin_type == iopin.PinType.RELAY and pin.direction == iopin.Direction.IN:
                pass
            else:
                # We have an output
                with pytest.raises(canlib.IoPinConfigurationNotConfirmed):
                    pin.value = 1


@pytest.mark.feature(features.iopin)
def test_confirmed(iopin_no):
    with canlib.openChannel(iopin_no) as iopin_ch:
        examined_classes = []
        try:
            iopin_ch.io_confirm_config()
        except canlib.IoNoValidConfiguration:
            assert iopin_ch.number_of_io_pins() == 0
        for pin in iopin_ch.io_pins():
            if type(pin).__name__ in examined_classes:
                continue

            examined_classes.append(type(pin).__name__)
            print(pin)
            if pin.pin_type == iopin.PinType.ANALOG and pin.direction == iopin.Direction.IN:
                hysteresis = pin.hysteresis
                value = 6
                pin.hysteresis = value
                assert value == pin.hysteresis
                pin.hysteresis = hysteresis

                lp_filter_order = pin.lp_filter_order
                pin.lp_filter_order = value
                assert value == pin.lp_filter_order
                pin.lp_filter_order = lp_filter_order

                value = pin.value

            elif pin.pin_type == iopin.PinType.DIGITAL and pin.direction == iopin.Direction.IN:
                high_low_filter = pin.high_low_filter
                if pin.module_type != iopin.ModuleType.INTERNAL:
                    value = 6
                    pin.high_low_filter = value
                    assert value == pin.high_low_filter
                    pin.high_low_filter = high_low_filter

                low_high_filter = pin.low_high_filter
                if pin.module_type != iopin.ModuleType.INTERNAL:
                    value = 6
                    pin.low_high_filter = value
                    assert value == pin.low_high_filter
                    pin.low_high_filter = low_high_filter

                if pin.module_type == iopin.ModuleType.INTERNAL:
                    iopin_ch.busOn()
                value = pin.value
            elif pin.pin_type == iopin.PinType.RELAY and pin.direction == iopin.Direction.IN:
                value = pin.value
            else:
                # We have an output
                if pin.module_type == iopin.ModuleType.INTERNAL:
                    iopin_ch.device().open_channel(chan_no_on_card=1).busOn()
                pin.value = 1
                assert pin.value == 1
                pin.value = 0
                assert pin.value < 1  # Analog pins don't give zero


@pytest.mark.parametrize(
    "module_type, expected_names",
    [
        (iopin.ModuleType.ANALOG, ['AO1', 'AO2', 'AO3', 'AO4', 'AI1', 'AI2', 'AI3', 'AI4']),
        (
            iopin.ModuleType.DIGITAL,
            [
                'DO1',
                'DO2',
                'DO3',
                'DO4',
                'DO5',
                'DO6',
                'DO7',
                'DO8',
                'DO9',
                'DO10',
                'DO11',
                'DO12',
                'DO13',
                'DO14',
                'DO15',
                'DO16',
                'DI1',
                'DI2',
                'DI3',
                'DI4',
                'DI5',
                'DI6',
                'DI7',
                'DI8',
                'DI9',
                'DI10',
                'DI11',
                'DI12',
                'DI13',
                'DI14',
                'DI15',
                'DI16',
            ],
        ),
        (
            iopin.ModuleType.RELAY,
            [
                'R1',
                'R2',
                'R3',
                'R4',
                'R5',
                'R6',
                'R7',
                'R8',
                'DI1',
                'DI2',
                'DI3',
                'DI4',
                'DI5',
                'DI6',
                'DI7',
                'DI8',
            ],
        ),
        (iopin.ModuleType.INTERNAL, ['DO1', 'DI1']),
    ],
)
def test_module_pin_names(module_type, expected_names):
    assert iopin.module_pin_names(module_type) == expected_names


def test_unvalid_module_pin_names():
    module_type = "Unknown type"
    with pytest.raises(AttributeError):
        iopin.module_pin_names(module_type)


@pytest.mark.feature(features.iopin)
def test_configuration(iopin_no):
    with canlib.openChannel(iopin_no) as iopin_ch:
        config = iopin.Configuration(iopin_ch)
        if config.modules[0].module_type == iopin.ModuleType.INTERNAL:
            expected_names = ['DO1', 'DI1']
            for i, pin in enumerate(config):
                assert config.index(expected_names[i]) == i
                assert config.name(i) == expected_names[i]
                assert config.pin(name=expected_names[i]) == pin


def test_config_issubset(iopin_no):
    with canlib.openChannel(iopin_no) as iopin_ch:
        config = iopin.Configuration(iopin_ch)
        if config.modules[0].module_type == iopin.ModuleType.INTERNAL:
            config_spec = [iopin.AddonModule(module_type=iopin.ModuleType.ANALOG)]
            assert not config.issubset(config_spec)
            config_spec = [iopin.AddonModule(module_type=iopin.ModuleType.INTERNAL)]
            assert config.issubset(config_spec)
