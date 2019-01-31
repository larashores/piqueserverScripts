from platforms.states.trigger.triggerstate import TriggerState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.states.needsbothstate import NeedsBothState
from platforms.worldobjects.trigger.presstrigger import PressTrigger
from platforms.worldobjects.trigger.distancetrigger import DistanceTrigger
from platforms.worldobjects.trigger.heighttrigger import HeightTrigger
from platforms.worldobjects.trigger.timertrigger import TimerTrigger
from platforms.util.strings import S_COMMAND_CANCEL
import enum


class TriggerType(enum.Enum):
    PRESS = PressTrigger
    DISTANCE = DistanceTrigger
    HEIGHT = HeightTrigger
    TIMER = TimerTrigger

    def __str__(self):
        return self.name.lower()


class AddTriggerState(NeedsButtonState, TriggerState):
    def __init__(self, negate, clear_others, trigger_type, *args, **kwargs):
        super().__init__()
        self._trigger_type = trigger_type
        self._negate = negate
        self._clear_others = clear_others
        self._args = args
        self._kwargs = kwargs

    def on_exit(self):
        if not self._button:
            return S_COMMAND_CANCEL.format(command='trigger {}'.format(self._trigger_type))
        trigger = self._make_trigger()
        if trigger is None:
            return
        trigger.negate = self._negate

        if self._clear_others:
            self._button.clear_triggers()
        self._button.add_trigger(trigger)
        return "Added {} trigger to button '{}'".format(self._trigger_type, self._button.label)

    def _make_trigger(self):
        return self._trigger_type.value(self.player.protocol, self._negate, *self._args, **self._kwargs)


class PlatformAddTriggerState(NeedsBothState, AddTriggerState):
    def on_exit(self):
        if not self._platform:
            return S_COMMAND_CANCEL.format(command='action {} '.format(self._trigger_type))
        return AddTriggerState.on_exit(self)

    def _make_trigger(self):
        return self._trigger_type.value(self.player.protocol, self._negate, self._platform, *self._args, **self._kwargs)


class PlayerAddTriggerState(AddTriggerState):
    def _make_trigger(self):
        return self._trigger_type.value(self.player.protocol, self._negate, self._button, *self._args, **self._kwargs)
