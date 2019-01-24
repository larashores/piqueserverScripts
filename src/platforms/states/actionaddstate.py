from platforms.commands.action.platformaction import PlatformAction, PLATFORM_ACTION_FUNCTIONS
from platforms.commands.action.playeraction import PlayerAction, PLAYER_ACTION_FUNCTIONS
from platforms.states.state import State
from platforms.strings import *

S_ACTION_ADDED = "Added {action} action to button '{label}'"


class ActionAddState(State):
    name = 'action'
    platform = None
    button = None

    def __init__(self, action, add = True):
        self.action = action
        self.add = add

    def on_exit(self, protocol, player):
        button = self.button
        if not button:
            return S_COMMAND_CANCEL.format(command = self.name)

        if self.action in PLATFORM_ACTION_FUNCTIONS:
            if not self.platform:
                return S_COMMAND_CANCEL.format(command=self.name)
            new_action = PlatformAction(protocol, self.platform.id, self.action, self.kwargs)
        elif self.action in PLAYER_ACTION_FUNCTIONS:
            new_action = PlayerAction(protocol, self.action, self.kwargs)

        if not self.add:
            button.actions = []
        button.actions.append(new_action)
        return S_ACTION_ADDED.format(action = self.action, label = button.label)
