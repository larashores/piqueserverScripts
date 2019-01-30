from platforms.states.action.actionstate import ActionState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.util.strings import S_COMMAND_CANCEL
from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta


class _ActionCommandState(NeedsButtonState, ActionState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self):
        if not self._button:
            return S_COMMAND_CANCEL.format(self.COMMAND_NAME)
        return self._on_activate_command()

    @abstractmethod
    def _on_activate_command(self):
        pass


class ActionListState(_ActionCommandState):
    COMMAND_NAME = 'action list'

    def _on_activate_command(self):
        if not self._button.actions:
            return "Button '{}' has no actions".format(self._button.label)
        items = ' -- '.join('#{} {}'.format(i, action) for i, action in enumerate(self._button.actions))
        return "Actions in '{}': ".format(self._button.label) + items


class ActionDelState(_ActionCommandState):
    COMMAND_NAME = 'action del'

    def __init__(self, number):
        _ActionCommandState.__init__(self)
        self._number = number

    def _on_activate_command(self):
        if self._number == 'all':
            self._button.actions.clear()
            return "Deleted all actions in button '{}'".format(self._button.label)
        try:
            action = self._button.pop_action(self._number)
            return "{} action {} deleted from button '{}'".format(action.NAME.upper(), self._number, self._button.label)
        except IndexError:
            return "Invalid action number! Use '/action list' to check"
