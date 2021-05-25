"""create_db.py -- Creating a .dbc database from scratch

This script will use canlib.kvadblib to create a new database file filled with
arbitrary data.

"""

import argparse
from collections import namedtuple

from canlib import kvadblib

Message = namedtuple('Message', 'name id dlc signals')
Signal = namedtuple('Signal', 'name size scaling limits unit')
EnumSignal = namedtuple('EnumSignal', 'name size scaling limits unit enums')

_messages = [
    Message(
        name='EngineData',
        id=100,
        dlc=8,
        signals=[
            Signal(
                name='PetrolLevel',
                size=(24, 8),
                scaling=(1, 0),
                limits=(0, 255),
                unit="l",
            ),
            Signal(
                name='EngPower',
                size=(48, 16),
                scaling=(0.01, 0),
                limits=(0, 150),
                unit="kW",
            ),
            Signal(
                name='EngForce',
                size=(32, 16),
                scaling=(1, 0),
                limits=(0, 0),
                unit="N",
            ),
            EnumSignal(
                name='IdleRunning',
                size=(23, 1),
                scaling=(1, 0),
                limits=(0, 0),
                unit="",
                enums={'Running': 0, 'Idle': 1},
            ),
            Signal(
                name='EngTemp',
                size=(16, 7),
                scaling=(2, -50),
                limits=(-50, 150),
                unit="degC",
            ),
            Signal(
                name='EngSpeed',
                size=(0, 16),
                scaling=(1, 0),
                limits=(0, 8000),
                unit="rpm",
            ),
        ],
    ),
    Message(
        name='GearBoxInfo',
        id=1020,
        dlc=1,
        signals=[
            Signal(
                name='EcoMode',
                size=(6, 2),
                scaling=(1, 0),
                limits=(0, 1),
                unit="",
            ),
            EnumSignal(
                name='ShiftRequest',
                size=(3, 1),
                scaling=(1, 0),
                limits=(0, 0),
                unit="",
                enums={'Shift_Request_On': 1, 'Shift_Request_Off': 0},
            ),
            EnumSignal(
                name='Gear',
                size=(0, 3),
                scaling=(1, 0),
                limits=(0, 5),
                unit="",
                enums={
                    'Idle': 0,
                    'Gear_1': 1,
                    'Gear_2': 2,
                    'Gear_3': 3,
                    'Gear_4': 4,
                    'Gear_5': 5,
                },
            ),
        ],
    ),
]


def create_database(name, filename):
    db = kvadblib.Dbc(name=name)

    for _msg in _messages:
        message = db.new_message(
            name=_msg.name,
            id=_msg.id,
            dlc=_msg.dlc,
        )

        for _sig in _msg.signals:
            if isinstance(_sig, EnumSignal):
                _type = kvadblib.SignalType.ENUM_UNSIGNED
                _enums = _sig.enums
            else:
                _type = kvadblib.SignalType.UNSIGNED
                _enums = {}
            message.new_signal(
                name=_sig.name,
                type=_type,
                byte_order=kvadblib.SignalByteOrder.INTEL,
                mode=kvadblib.SignalMultiplexMode.MUX_INDEPENDENT,
                size=kvadblib.ValueSize(*_sig.size),
                scaling=kvadblib.ValueScaling(*_sig.scaling),
                limits=kvadblib.ValueLimits(*_sig.limits),
                unit=_sig.unit,
                enums=_enums,
            )

    db.write_file(filename)
    db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a database from scratch.")
    parser.add_argument('filename', help=("The filename to save the database to."))
    parser.add_argument(
        '-n',
        '--name',
        default='Engine example',
        help=("The name of the database (not the filename, the internal name."),
    )
    args = parser.parse_args()

    create_database(args.name, args.filename)
