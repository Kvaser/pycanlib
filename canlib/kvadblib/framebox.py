from .. import CanlibException
from .message import Message


class SignalNotFound(CanlibException):
    def __init__(self, text):
        super().__init__(self, text)


class FrameBox:
    """Helper class for sending signals

    This class allows sending signals without worrying about what message they
    are defined in. It does this by binding a message and all its signals to
    the same `canlib.Frame` object.

    Objects are created by giving them a `Dbc` database, and optionally a list
    of messages (either names or `Message` objects)::

      db = Dbc(...)
      framebox = FrameBox(db, messages=('Msg0','Msg1'))

    Messages can also be added after instantiation with `add_message`::

      framebox.add_message('Msg0', 'Msg1')

    Then setting signal values for any added message is done with::

      framebox.signal('Sig0').phys = 7
      framebox.signal('Sig1').phys = 20

    Once all values are set, they can easily be sent via the channel `channel` with::

      for frame in framebox.frames():
        channel.write(frame)

    Any `Framebox` methods that return messages requires the message to have
    been added to the framebox, either with the ``messages`` constructor
    argument or with `add_message`. Likewise, any methods that return signals
    require the signal's message to have been added.

    """

    def __init__(self, db, messages=()):
        self._db = db
        self._bsigs = {}
        self._bmsgs = {}

        for message in messages:
            self.add_message(message)

    def add_message(self, message):
        """Add a message to the framebox

        The message will be available for all future uses of `FrameBox.message`
        and `FrameBox.messages`, and all its signals will be available for uses
        of `FrameBox.signal` and `FrameBox.signals`.

        The ``message`` argument can either be a message name, or a
        `canlib.kvadblib.Message` object.

        """
        if not isinstance(message, Message):
            message = self._db.get_message_by_name(message)
        self._add_msg(message)

    def signal(self, name):
        """Retrieves a signal by name

        Returns a `BoundSignal` that shares its `canlib.Frame` object with its
        parent message and sibling signals.

        """
        try:
            return self._bsigs[name]
        except KeyError:
            raise SignalNotFound("Framebox has no signal named " + repr(name))

    def signals(self):
        """Iterator over all signals that this `FrameBox` is aware of"""
        return iter(self._bsigs.values())

    def message(self, name):
        """Retrieves a message by name

        Returns a `BoundMessage` that shares its `canlib.Frame` object with its
        child signals.

        """
        if name not in self._bmsgs:
            self._add_msg(self._db.get_message_by_name(name))
        return self._bmsgs[name]

    def messages(self):
        """Iterator over all messages that this `FrameBox` is aware of"""
        return iter(self._bmsgs.values())

    def frames(self):
        """Iterate over all frames of the signals/messages from this `FrameBox`"""
        return (bmsg._frame for bmsg in self._bmsgs.values())

    def _add_msg(self, message):
        assert message.name not in self._bmsgs
        bmsg = message.bind()
        self._bmsgs[message.name] = bmsg
        for bsig in bmsg:
            self._bsigs[bsig.name] = bsig
