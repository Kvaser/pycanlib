# examine_db.py
"""

This script uses canlib.kvadblib to parse a database and print its contents.

"""
import argparse
import sys

from canlib import kvadblib

INDENT = ' ' * 4


def print_db(db):
    print('DATABASE')
    print(db.name)
    for line in db_lines(db):
        print(INDENT + line)


def adef_lines(adef):
    yield 'type: ' + type(adef).__name__
    yield 'definition: ' + str(adef.definition)
    yield 'owner: ' + str(adef.owner)


def attr_lines(attrib):
    yield str(attrib.name) + ' = ' + str(attrib.value)


def db_lines(db):
    yield 'flags: ' + str(db.flags)
    yield 'protocol: ' + str(db.protocol)
    yield ''

    yield 'ATTRIBUTE DEFINITIONS'
    for adef in db.attribute_definitions():
        yield str(adef.name)
        for line in adef_lines(adef):
            yield INDENT + line
    yield ''

    yield 'MESSAGES'
    for message in db:
        yield str(message.name)
        for line in msg_lines(message):
            yield INDENT + line
    yield ''


def enum_lines(enums):
    for name, val in enums.items():
        yield str(name) + ' = ' + str(val)


def msg_lines(message):
    yield 'id: ' + str(message.id)
    yield 'flags: ' + str(message.flags)
    yield 'dlc: ' + str(message.dlc)
    yield 'comment: ' + str(message.comment)
    yield ''

    yield 'ATTRIBUTES'
    for attr in message.attributes():
        for line in attr_lines(attr):
            yield line
    yield ''

    yield 'SIGNALS'
    for signal in message:
        yield str(signal.name)
        for line in sig_lines(signal):
            yield INDENT + line
    yield ''


def sig_lines(signal):
    for name in ('type', 'byte_order', 'mode', 'size', 'scaling', 'limits', 'unit', 'comment'):
        yield name + ': ' + str(getattr(signal, name))
    yield ''

    try:
        enums = signal.enums
    except AttributeError:
        pass
    else:
        yield 'ENUMERATIONS'
        for line in enum_lines(enums):
            yield line
        yield ''

    yield 'ATTRIBUTES'
    for attr in signal.attributes():
        for line in attr_lines(attr):
            yield line
    yield ''


def examine_database(db_name):
    with kvadblib.Dbc(filename=db_name) as db:
        print_db(db)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument(
        'db', type=str, metavar='<database.dbc>', help='The dbc database file to examine.'
    )
    args = parser.parse_args()

    examine_database(args.db)
