from playerstates.signal import Signal
from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.worldobjects.platform import Platform
from piqueserver.player import FeatureConnection

import enum


#  The must be in a list or else enum will count them as functions not enumerations
class ActionType(enum.Enum):
    HEIGHT = [Platform.set_height]
    RAISE = [Platform.raise_]
    LOWER = [Platform.lower]
    ELEVATOR = [Platform.set_height]
    CHAT = [FeatureConnection.send_chat]
    TELEPORT = [FeatureConnection.set_location]
    DAMAGE = [FeatureConnection.hit]

    def __str__(self):
        return self.name.lower()


class Action(metaclass=ABCMeta):
    NAME = abstractattribute

    def __init__(self, action_type, *args, **kwargs):
        self.signal_remove = Signal()
        self._action_type = action_type
        self._args = args
        self._kwargs = kwargs

    def destroy(self):
        self.signal_remove(self)
        self.signal_remove.clear()

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
