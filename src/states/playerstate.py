from states.signal import Signal
from abc import ABCMeta


class PlayerState(metaclass=ABCMeta):
    BLOCKING_STATE = False

    def __init__(self, player, parent_state=None):
        self.signal_exit = Signal()
        self.player = player
        self.parent_state = parent_state if parent_state else self

    def on_enter(self):
        pass

    def on_exit(self):
        pass
