from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.states.trigger.triggerstate import TriggerState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.worldobjects.button import LogicType
from platforms.util.strings import *


class _TriggerCommandState(NeedsButtonState, TriggerState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self):
        if not self._button:
            return S_COMMAND_CANCEL.format(self.COMMAND_NAME)
        return self._on_activate_command()

    @abstractmethod
    def _on_activate_command(self):
        pass


class TriggerListState(_TriggerCommandState):
    COMMAND_NAME = 'trigger list'

    def _on_activate_command(self):
        return self._button.get_trigger_info()


class TriggerDeleteState(_TriggerCommandState):
    COMMAND_NAME = 'del'

    def __init__(self, number):
        _TriggerCommandState.__init__(self)
        self._number = number

    def _on_activate_command(self):
        if self._number == 'all':
            self._button.clear_triggers()
            return "Deleted all triggers in button '{}'".format(self._button.label)
        try:
            trigger = self._button.pop_trigger(self._number)
            return "{} trigger {} deleted from button '{}'".format(trigger.NAME.upper(),
                                                                   self._number, self._button.label)
        except IndexError:
            return "Invalid trigger number! Use '/trigger list' to check"


class TriggerLogicState(_TriggerCommandState):
    COMMAND_NAME = 'logic'

    def __init__(self, logic):
        _TriggerCommandState.__init__(self)
        self._logic = logic

    def _on_activate_command(self):
        self._button.logic = self._logic
        self._button.trigger_check()
        return "Button '{}' will activate when {}".format(self._button.label,
                                                          'ALL its triggers yield true'
                                                          if self._logic == LogicType.AND
                                                          else 'ANY of its triggers fire')
