from .bound_signal import BoundSignal


class BoundMessage:
    """A CAN data object that manipulates data through signals."""

    def __init__(self, message, frame):
        """Create an object representing a message bound to a frame

        Args:
            message (`kvadblib.Message`): The message to be bound
            frame (`Frame`): The frame containing CAN data

        """
        self._message = message
        self._frame = frame

    @property
    def _data(self):
        return self._frame.data

    @_data.setter
    def _data(self, val):
        self._frame.data = val

    def __getattr__(self, attr):
        signal = BoundSignal(
            signal=self._message.get_signal(name=attr),
            frame=self._frame,
        )
        return signal

    def __iter__(self):
        for signal in self._message:
            yield BoundSignal(
                signal=signal,
                frame=self._frame,
            )

    def __str__(self):
        msg_name = None
        if self._message is not None:
            msg_name = self._message.name
        return f"Frame: message_name:{msg_name}, data:{self._data}"
