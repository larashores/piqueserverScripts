from playerstates.signal import Signal
from abc import ABCMeta


class PlayerState(metaclass=ABCMeta):
    BLOCKING_STATE = False

    def __init__(self):
        self.signal_exit = Signal()
        self.player = None      # Should be set by StateStack on push

    def on_enter(self):
        pass

    def on_exit(self):
        pass
