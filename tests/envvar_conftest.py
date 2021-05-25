import os

import pytest
from tscript_wrap import ScriptRunner

from canlib import canlib

BITRATE = canlib.canBITRATE_1M
CHANNEL_FLAGS = 0


@pytest.fixture(scope="module")
def envvar_t(script_no_pair):
    channel_number = script_no_pair[0]
    datadir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    tscript_path = os.path.join(datadir, "txe", "envvar.txe")
    with ScriptRunner(channel_number, script_fp=tscript_path, slot=0) as envvar_t:
        yield envvar_t
        envvar_t.print_output()


@pytest.fixture
def pycan_ch(script_no_pair):
    channel_number = script_no_pair[1]
    with canlib.openChannel(channel_number, bitrate=BITRATE, flags=CHANNEL_FLAGS) as pycan_ch:
        pycan_ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        pycan_ch.busOn()
        # The CAN bus should initially be empty
        with pytest.raises(canlib.CanNoMsg):
            _ = pycan_ch.read()
        yield pycan_ch
        pycan_ch.busOff()


@pytest.fixture
def char_text_1():
    text = """\
The arguments can be primitive data types or compound data types. Do you
have any idea why this is not working? Messages can be sent to and received
from ports, but these messages must obey the so-called "port protocol." Its
main implementation is the Glasgow Haskell Compiler. Ports are created with the
built-in function open_port. Atoms can contain any character if they are
enclosed within single quotes and an escape convention exists which allows any
character to be used within an atom. Atoms can contain any character if they
are enclosed within single quotes and an escape convention exists which allows
any character to be used within an atom. He looked inquisitively at his
keyboard and wrote another sentence. Ports are created with the built-in
function open_port. He looked inquisitively at his keyboard and wrote another
sentence. The Galactic Empire is nearing completion of the Death Star, a space
station with the power to destroy entire planets. The Galactic Empire is
nearing completion of the Death Star, a space station with the power to destroy
entire planets. The sequential subset of Erlang supports eager evaluation,
single assignment, and dynamic typing. Its main implementation is the Glasgow
Haskell Compiler. Ports are created with the built-in function open_port. Its
main implementation is the Glasgow Haskell Compiler. The sequential subset of
Erlang supports eager evaluation, single assignment, and dynamic typing. Any
element of a tuple can be accessed in constant time. Type classes first
appeared in the Haskell programming language. Haskell is a standardized,
general-purpose purely functional programming language, with non-strict
semantics and strong static typing. Erlang is a general-purpose, concurrent,
functional programming language. Ports are used to communicate with the
external world. In 1989 the building was heavily damaged by fire, but it has
since been restored. Any element of a tuple can be accessed in constant
time. Its main implementation is the Glasgow Haskell Compiler. Haskell features
a type system with type inference and lazy evaluation. The Galactic Empire is
nearing completion of the Death Star, a space station with the power to destroy
entire planets. Do you have any idea why this is not working? Haskell features
a type system with type inference and lazy evaluation. They are written as
strings of consecutive alphanumeric characters, the first character being
lowercase. Type classes first appeared in the Haskell programming
language. Type classes first appeared in the Haskell programming language. He
looked inquisitively at his keyboard and wrote another sentence. Make me a
sandwich. Atoms can contain any character if they are enclosed within single
quotes and an escape convention exists which allows any character to be used
within an atom. Messages can be sent to and received from ports, but these
messages must obey the so-called "port protocol." The arguments can be
primitive data types or compound data types. The Galactic Empire is nearing
completion of the Death Star, a space station with the power to destroy entire
planets. The sequential subset of Erlang supports eager evaluation, single
assignment, and dynamic typing. Ports are created with the built-in function
open_port. Ports are used to communicate with the external world. Atoms are
used within a program to denote distinguished values. The syntax {D1,D2,...,Dn}
denotes a tuple whose arguments are D1, D2, ... Dn. Do you come here often? The
sequential subset of Erlang supports eager evaluation, single assignment, and
dynamic typing. Its main implementation is the Glasgow Haskell Compiler. The
arguments can be primitive data types or compound data types. The Galactic
Empire is nearing completion of the Death Star, a space station with the power
to destroy entire planets. Make me a sandwich. Where are my pants? Where are my
pants? I don\'t even care. Initially composing light-hearted and irreverent
works, he also wrote serious, sombre and religious pieces beginning in the
1930s. In 1989 the building was heavily damaged by fire... m"""

    assert len(text) == canlib.ENVVAR_MAX_SIZE
    return text


@pytest.fixture
def char_text_2():
    text = """\
A syntax {D1,D2,...,Dn} denotes a tuple whose arguments are D1, D2,
... Dn. Ports are created with the built-in function open_port. Any element of
a tuple can be accessed in constant time. Haskell features a type system with
type inference and lazy evaluation. Atoms are used within a program to denote
distinguished values. Atoms are used within a program to denote distinguished
values. Atoms can contain any character if they are enclosed within single
quotes and an escape convention exists which allows any character to be used
within an atom. He looked inquisitively at his keyboard and wrote another
sentence. Haskell features a type system with type inference and lazy
evaluation. Do you have any idea why this is not working? Atoms can contain any
character if they are enclosed within single quotes and an escape convention
exists which allows any character to be used within an atom. Erlang is known
for its designs that are well suited for systems. Atoms are used within a
program to denote distinguished values. The arguments can be primitive data
types or compound data types. Do you come here often? Do you come here often?
Erlang is known for its designs that are well suited for systems. Any element
of a tuple can be accessed in constant time. He looked inquisitively at his
keyboard and wrote another sentence. The sequential subset of Erlang supports
eager evaluation, single assignment, and dynamic typing. The arguments can be
primitive data types or compound data types. She spent her earliest years
reading classic literature, and writing poetry. The syntax {D1,D2,...,Dn}
denotes a tuple whose arguments are D1, D2, ... Dn. The Galactic Empire is
nearing completion of the Death Star, a space station with the power to destroy
entire planets. Do you come here often? Initially composing light-hearted and
irreverent works, he also wrote serious, sombre and religious pieces beginning
in the 1930s. Tuples are containers for a fixed number of Erlang data
types. Atoms can contain any character if they are enclosed within single
quotes and an escape convention exists which allows any character to be used
within an atom. She spent her earliest years reading classic literature, and
writing poetry. Do you have any idea why this is not working? The Galactic
Empire is nearing completion of the Death Star, a space station with the power
to destroy entire planets. The Galactic Empire is nearing completion of the
Death Star, a space station with the power to destroy entire planets. Erlang is
a general-purpose, concurrent, functional programming language. They are
written as strings of consecutive alphanumeric characters, the first character
being lowercase. Ports are created with the built-in function
open_port. Haskell features a type system with type inference and lazy
evaluation. Atoms can contain any character if they are enclosed within single
quotes and an escape convention exists which allows any character to be used
within an atom. Haskell features a type system with type inference and lazy
evaluation. Where are my pants? Haskell features a type system with type
inference and lazy evaluation. Do you have any idea why this is not working?
Tuples are containers for a fixed number of Erlang data types. Messages can be
sent to and received from ports, but these messages must obey the so-called
"port protocol." They are written as strings of consecutive alphanumeric
characters, the first character being lowercase. Initially composing
light-hearted and irreverent works, he also wrote serious, sombre and religious
pieces beginning in the 1930s. Messages can be sent to and received from ports,
but these messages must obey the so-called "port protocol." The syntax
{D1,D2,...,Dn} denotes a tuple whose arguments are D1, D2, ... Dn. I don\'t
even care. The Galactic Empire is nearing completion of the Death Star, a space
station with the power to destroy entire planets. Haskell features a type
system with type inference and lazy evaluation. The Galactic Empire is nearing
completion of the Death Star, a space station with the power to destroy a..."""

    assert len(text) == canlib.ENVVAR_MAX_SIZE
    return text
