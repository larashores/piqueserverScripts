from platforms.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.states.trigger.triggerstate import TriggerState
from platforms.states.needsplatformstate import NeedsPlatformState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.worldobjects.trigger.presstrigger import PressTrigger
from platforms.worldobjects.trigger.distancetrigger import DistanceTrigger
from platforms.worldobjects.trigger.tracktrigger import TrackTrigger
from platforms.worldobjects.trigger.heighttrigger import HeightTrigger
from platforms.strings import S_COMMAND_CANCEL


class TriggerAddState(NeedsButtonState, TriggerState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def __init__(self, negate, clear_others):
        super().__init__()
        self.negate = negate
        self.clear_others = clear_others

    def on_exit(self):
        if not self.button:
            return S_COMMAND_CANCEL.format(command='trigger {}'.format(self.COMMAND_NAME))

        trigger = self._make_trigger()
        if trigger is None:
            return
        trigger.negate = self.negate

        if self.clear_others:
            self.button.clear_triggers()
        self.button.add_trigger(trigger)
        return "Added {} trigger to button '{}'".format(self.COMMAND_NAME.lower(), self.button.label)

    @abstractmethod
    def _make_trigger(self):
        pass


class PressTriggerState(TriggerAddState):
    COMMAND_NAME = 'press'

    def _make_trigger(self):
        return PressTrigger(self.player.protocol)


class DistanceTriggerState(TriggerAddState):
    COMMAND_NAME = 'distance'

    def __init__(self, radius, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius

    def _make_trigger(self):
        return DistanceTrigger(self.player.protocol, self.button, self.radius)


class TrackTriggerState(TriggerAddState):
    COMMAND_NAME = 'track'

    def __init__(self, radius, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius

    def _make_trigger(self):
        return TrackTrigger(self.player.protocol, self.radius)


class HeightTriggerState(NeedsPlatformState, TriggerAddState):
    COMMAND_NAME = 'height'

    def __init__(self, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height = height

    def _make_trigger(self):
        if not self.platform:
            return None
        return HeightTrigger(self.player.protocol, self.platform.id, self.height)
