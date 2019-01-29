from platforms.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.states.trigger.triggerstate import TriggerState
from platforms.states.needsplatformstate import NeedsPlatformState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.worldobjects.trigger.presstrigger import PressTrigger
from platforms.worldobjects.trigger.distancetrigger import DistanceTrigger
from platforms.worldobjects.trigger.tracktrigger import TrackTrigger
from platforms.worldobjects.trigger.heighttrigger import HeightTrigger
from platforms.strings import S_COMMAND_CANCEL
import enum


class TriggerType(enum.Enum):
    PRESS = PressTrigger
    DISTANCE = DistanceTrigger
    TRACK = TrackTrigger
    HEIGHT = HeightTrigger

    def __str__(self):
        return self.name.lower()


class TriggerAddState(NeedsButtonState, TriggerState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def __init__(self, trigger_type, negate, clear_others, *args, **kwargs):
        super().__init__()
        self._trigger_type = trigger_type
        self._negate = negate
        self._clear_others = clear_others
        self._args = args
        self._kwargs = kwargs

    def on_exit(self):
        if not self.button:
            return S_COMMAND_CANCEL.format(command='trigger {}'.format(self._trigger_type))

        trigger = self._trigger_type.value(self.player.protocol, *self._args, **self._kwargs)
        if trigger is None:
            return
        trigger.negate = self._negate

        if self._clear_others:
            self.button.clear_triggers()
        self.button.add_trigger(trigger)
        return "Added {} trigger to button '{}'".format(self._trigger_type, self.button.label)
