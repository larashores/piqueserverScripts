from playerstates.signal import Signal
from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta


class Action(metaclass=ABCMeta):
    NAME = abstractattribute

    def __init__(self):
        self.signal_remove = Signal()

    def destroy(self):
        self.signal_remove(self)
        self.signal_remove.clear()

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
