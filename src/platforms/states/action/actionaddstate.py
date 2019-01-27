from platforms.abstractattribute import abstractmethod, ABCMeta
from platforms.worldobjects.action.platformaction import PlatformAction
from platforms.worldobjects.action.playeraction import PlayerAction
from platforms.states.action.actionstate import ActionState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.strings import *


class ActionAddState(ActionState, NeedsButtonState, metaclass=ABCMeta):
    def __init__(self, action_type, clear_others=True, **kwargs):
        NeedsButtonState.__init__(self)
        self.action_type = action_type
        self.clear_others = clear_others
        self.platform = None
        self.kwargs = kwargs

    def on_exit(self):
        if not self.button:
            return S_COMMAND_CANCEL.format(command='action')
        action = self._make_action()
        if action is None:
            return S_COMMAND_CANCEL.format(command='action {}'.format(self.action_type.name.lower()))

        if not self.clear_others:
            self.button.actions.clear()
        self.button.actions.append(action)
        return "Added {} action to button '{}'".format(self.action_type.value, self.button.label)

    @abstractmethod
    def _make_action(self):
        pass


class PlatformActionAddState(ActionAddState):
    def _make_action(self):
        return (PlatformAction(self.player.protocol, self.platform.id, self.action_type, self.kwargs)
                if self.platform else None)


class PlayerActionAddState(ActionAddState):
    def _make_action(self):
        return PlayerAction(self.player.protocol, self.action_type, self.kwargs)
