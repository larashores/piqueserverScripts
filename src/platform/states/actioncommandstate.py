from platform.states.state import State
from platform.strings import S_COMMAND_CANCEL

S_ACTION_LIST_EMPTY = "Button '{label}' has no actions"
S_ACTION_LIST_HEADER = "Actions in '{label}': "
S_ACTION_DELETED = "{action} action {number} deleted from button '{label}'"
S_ACTION_DELETED_ALL = "Deleted all actions in button '{label}'"
S_ACTION_INVALID_NUMBER = "Invalid action number! Use '/action list' to check"


class ActionCommandState(State):
    name = 'action'
    button = None

    def __init__(self, command):
        self.command = command

    def on_exit(self, protocol, player):
        button = self.button
        if not button:
            return S_COMMAND_CANCEL.format(command = 'action ' + self.command)

        if self.command == 'list':
            if not button.actions:
                return S_ACTION_LIST_EMPTY.format(label = button.label)

            items = ' -- '.join('#{} {}'.format(i, action) for i, action in enumerate(button.actions))
            return S_ACTION_LIST_HEADER.format(label=button.label) + items
        elif self.command == 'del':
            if self.number == 'all':
                button.actions = []
                return S_ACTION_DELETED_ALL.format(label = button.label)
            else:
                try:
                    index = self.number % len(button.actions)
                    action = button.actions.pop(self.number)
                except IndexError:
                    return S_ACTION_INVALID_NUMBER

                action_type = action.type.capitalize()
                return S_ACTION_DELETED.format(action=action_type, number=index, label=button.label)
