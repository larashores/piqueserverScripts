from platforms.states.action.actionstate import ActionState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.strings import S_COMMAND_CANCEL
from platforms.abstractattribute import abstractattribute, abstractmethod, ABCMeta


class ActionCommandState(ActionState, NeedsButtonState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self, protocol, player):
        button = self.button
        if not button:
            return S_COMMAND_CANCEL.format(command='action {}'.format(self.COMMAND_NAME))
        self._on_activate_command(protocol, player)

    @abstractmethod
    def _on_activate_command(self, protocol, player):
        pass


class ActionListState(ActionCommandState):
    COMMAND_NAME = 'list'

    def _on_activate_command(self, protocol, player):
        if not self.button.actions:
            return "Button '{}' has no actions".format(self.button.label)
        items = ' -- '.join('#{} {}'.format(i, action) for i, action in enumerate(self.button.actions))
        return "Actions in '{}': ".format(self.button.label) + items


class ActionDelState(ActionCommandState):
    COMMAND_NAME = 'del'

    def __init__(self, number):
        ActionCommandState.__init__(self)
        self.number = number

    def _on_activate_command(self, protocol, player):
        if self.number == 'all':
            self.button.actions.clear()
            return "Deleted all actions in button '{}'".format(self.button.label)
        try:
            index = self.number % len(self.button.actions)
            action = self.button.actions.pop(self.number)
            return "{} action {} deleted from button '{}'".format(action.type.capitalize(), index, self.button.label)
        except IndexError:
            return "Invalid action number! Use '/action list' to check"
