class BoundSignal:
    def __init__(self, signal, frame):
        self.frame = frame
        self.signal = signal

    def __str__(self):
        txt = f"<{self.__class__.__name__}: name={self.name!r}, phys={self.phys!r}>"
        if self.unit:
            txt += f", unit:{self.unit}"
        return txt

    @property
    def phys(self):
        """`int` or `float`: Signal's physical value"""
        value = self.signal.phys_from(self.frame.data)
        return value

    @phys.setter
    def phys(self, value):
        self.frame.data = self.signal.data_from(self.frame.data, phys=value)

    @property
    def raw(self):
        """`int`: Signal's raw value"""
        value = self.signal.raw_from(self.frame.data)
        return value

    @raw.setter
    def raw(self, value):
        self.frame.data = self.signal.data_from(self.frame.data, raw=value)

    @property
    def unit(self):
        """`str`: Signal's unit string"""
        return self.signal.unit

    @property
    def name(self):
        """`str`: Signal's name string"""
        return self.signal.name

    @property
    def value(self):
        """Signal's value

        If the signal is an enum-signal (i.e. the signal has a defined value
        table), then the enum name is returned if found, otherwise the signals
        raw value (`raw`) is returned. If the signal is not an enum-signal, the
        signals physical value (`phys`) is returned.

        .. versionadded:: 1.7

        """
        if self.is_enum:
            value = self.raw
            for key, val in self.signal.enums.items():
                if val == value:
                    val = key
                    break
            else:
                # Nothing found in enum, return raw value
                val = value
        else:
            val = self.phys

        return val

    @property
    def is_enum(self):
        """`bool`: Whether this signal is an enum-signal

        .. versionadded:: 1.7

        """
        return hasattr(self.signal, 'enums')
