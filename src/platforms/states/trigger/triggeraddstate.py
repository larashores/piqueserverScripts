from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.states.trigger.triggerstate import TriggerState
from platforms.states.needsplatformstate import NeedsPlatformState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.worldobjects.trigger.presstrigger import PressTrigger
from platforms.worldobjects.trigger.distancetrigger import DistanceTrigger
from platforms.worldobjects.trigger.tracktrigger import TrackTrigger
from platforms.worldobjects.trigger.heighttrigger import HeightTrigger
from platforms.util.strings import S_COMMAND_CANCEL
import enum


class TriggerType(enum.Enum):
    PRESS = PressTrigger
    DISTANCE = DistanceTrigger
    TRACK = TrackTrigger
    HEIGHT = HeightTrigger

    def __str__(self):
        return self.name.lower()


class _AddTriggerState(NeedsButtonState, TriggerState, metaclass=ABCMeta):
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

    @abstractmethod
    def _make_trigger(self):
        pass


class PlatformAddTriggerState(NeedsPlatformState, _AddTriggerState):
    def on_exit(self):
        if not self._platform:
            return S_COMMAND_CANCEL.format(command='action {} '.format(self._trigger_type))
        return _AddTriggerState.on_exit(self)

    def on_enter(self):
        self.player.send_chat(NeedsButtonState.on_enter(self))
        self.player.send_chat(NeedsPlatformState.on_enter(self))

    def _on_button_selected(self):
        if self._platform:
            self.signal_exit(self)
        else:
            self.player.send_chat("Button '{}' selected".format(self._button.label))

    def _on_platform_selected(self):
        if self._button:
            self.signal_exit(self)
        else:
            self.player.send_chat("Platform '{}' selected".format(self._platform.label))

    def _make_trigger(self):
        return self._trigger_type.value(self.player.protocol, self._button, self._platform, *self._args, **self._kwargs)


class PlayerAddTriggerState(_AddTriggerState):
    def _make_trigger(self):
        return self._trigger_type.value(self.player.protocol, self._button, *self._args, **self._kwargs)
