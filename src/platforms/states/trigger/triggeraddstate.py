from platforms.states.state import State
from platforms.commands.trigger.presstrigger import PressTrigger
from platforms.commands.trigger.distancetrigger import DistanceTrigger
from platforms.commands.trigger.tracktrigger import TrackTrigger
from platforms.commands.trigger.heighttrigger import HeightTrigger
from platforms.strings import S_COMMAND_CANCEL

S_TRIGGER_ADDED = "Added {trigger} trigger to button '{label}'"


class TriggerAddState(State):
    name = 'trigger'
    platform = None
    button = None

    def __init__(self, trigger, negate, add = True):
        self.trigger = trigger
        self.negate = negate
        self.add = add

    def on_exit(self, protocol, player):
        button = self.button
        if not button:
            return S_COMMAND_CANCEL.format(command = self.name)

        if self.trigger == 'press':
            new_trigger = PressTrigger(protocol)
        elif self.trigger == 'distance':
            new_trigger = DistanceTrigger(protocol, self.radius)
        elif self.trigger == 'track':
            new_trigger = TrackTrigger(protocol, self.radius)
        elif self.trigger == 'height':
            if not self.platform:
                return S_COMMAND_CANCEL.format(command = self.name)
            new_trigger = HeightTrigger(protocol, self.platform.id, self.height)
        new_trigger.negate = self.negate

        if not self.add:
            button.clear_triggers()
        button.add_trigger(new_trigger)
        return S_TRIGGER_ADDED.format(trigger = self.trigger,label = button.label)