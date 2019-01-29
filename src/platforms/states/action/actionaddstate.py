from platforms.abstractattribute import abstractmethod, ABCMeta
from platforms.worldobjects.action.platformaction import PlatformAction
from platforms.worldobjects.action.playeraction import PlayerAction
from platforms.states.action.actionstate import ActionState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.states.needsplatformstate import NeedsPlatformState
from platforms.strings import *


class ActionAddState(NeedsButtonState, ActionState, metaclass=ABCMeta):
    def __init__(self, clear_others, function, *args, **kwargs):
        super().__init__()
        self._function = function
        self.action_type = 'test'
        self.clear_others = clear_others
        self.platform = None
        self.args = args
        self.kwargs = kwargs

    def on_exit(self):
        if not self.button:
            return S_COMMAND_CANCEL.format(command='action')
        action = self._make_action()
        if action is None:
            return S_COMMAND_CANCEL.format(command='action {}'.format(self.action_type.lower()))

        if not self.clear_others:
            self.button.clear_actions()
        self.button.add_action(action)
        return "Added {} action to button '{}'".format(self.action_type, self.button.label)

    @abstractmethod
    def _make_action(self):
        pass


class PlatformActionAddState(NeedsPlatformState, ActionAddState):
    def _make_action(self):
        return (PlatformAction(self.player.protocol, self.platform.id, self.action_type, self.kwargs)
                if self.platform else None)


class PlayerActionAddState(ActionAddState):
    def _make_action(self):
        return PlayerAction(self.player.protocol, self._function, *self.args, **self.kwargs)
