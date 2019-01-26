from platforms.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.states.trigger.triggerstate import TriggerState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.strings import *


class TriggerCommandState(TriggerState, NeedsButtonState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self, protocol, player):
        if not self.button:
            return S_COMMAND_CANCEL.format(command='trigger []'.format(self.COMMAND_NAME))
        self._on_activate_command(protocol, player)

    @abstractmethod
    def _on_activate_command(self, protocol, player):
        pass


class TriggerListState(TriggerCommandState):
    COMMAND_NAME = 'list'

    def _on_activate_command(self, protocol, player):
        if not self.button.triggers:
            return "Button '{}' has no triggers".format(self.button.label)

        item_list = ['#{} {}{}'.format(i, trigger, ' [CHECK]' if trigger.status else '')
                     for i, trigger in enumerate(self.button.triggers)]
        separator = ' AND ' if self.button.logic == 'and' else ' OR '
        return "Triggers in '{}': {}".format(self.button.label, separator.join(item_list))


class TriggerDeleteState(TriggerCommandState):
    COMMAND_NAME = 'del'

    def __init__(self, number):
        TriggerCommandState.__init__(self)
        self.number = number

    def _on_activate_command(self, protocol, player):
        if self.number == 'all':
            self.button.clear_triggers()
            return "Deleted all triggers in button '{}'".format(self.button.label)
        try:
            trigger = self.button.triggers[self.number]
            index = self.button.triggers.index(trigger)
            trigger.unbind()
            self.button.trigger_check()
            return "{} trigger {} deleted from button '{}'".format(trigger.type.capitalize(), index, self.button.label)
        except IndexError:
            return "Invalid trigger number! Use '/trigger list' to check"


class TriggerLogicState(TriggerCommandState):
    COMMAND_NAME = 'logic'

    def __init__(self, logic):
        TriggerCommandState.__init__(self)
        self.logic = logic

    def _on_activate_command(self, protocol, player):
        self.button.logic = self.logic
        self.button.trigger_check()
        return "Button '{}' will activate when {}".format(
            self.button.label, 'ALL its triggers yield true' if self.logic == 'and' else 'ANY of its triggers fire')


class TriggerQuietState(TriggerCommandState):
    COMMAND_NAME = 'quiet'

    def _on_activate_command(self, protocol, player):
        self.button.silent = not self.button.silent
        return "Button {} will {}".format(
            self.button.label, 'activate quietly' if self.button.silent else 'animate when activated')
