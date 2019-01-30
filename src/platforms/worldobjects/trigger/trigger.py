from playerstates.signal import Signal
from abc import abstractmethod, ABCMeta


class Trigger(metaclass=ABCMeta):
    NAME = None
    ONE_PER_BUTTON = False

    def __init__(self, protocol, button, negate=False):
        self.signal_fire = Signal()
        self._protocol = protocol
        self._negate = negate
        self._button = button

    def update(self, *args, **kwargs):
        pass

    def unbind(self):
        pass

    def get_status(self):
        return self._status() ^ self._negate

    def serialize(self):
        return {'type': self.NAME, 'negate': self._negate}

    def _status(self):
        return False
