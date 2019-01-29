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
        self._action_type = 'test'
        self._clear_others = clear_others
        self._args = args
        self._kwargs = kwargs

    def on_exit(self):
        if not self._button:
            return S_COMMAND_CANCEL.format(command='action')
        action = self._make_action()
        if action is None:
            return S_COMMAND_CANCEL.format(command='action {}'.format(self._action_type.lower()))

        if not self._clear_others:
            self.button.clear_actions()
        self.button.add_action(action)
        return "Added {} action to button '{}'".format(self._action_type, self.button.label)

    @abstractmethod
    def _make_action(self):
        pass


class PlatformActionAddState(NeedsPlatformState, ActionAddState):
    def on_exit(self):
        if not self._platform:
            return S_COMMAND_CANCEL.format(command='action')
        return ActionAddState.on_exit(self)

    def _make_action(self):
        return PlatformAction(self.platform, self._function, *self._args, **self._kwargs)


class PlayerActionAddState(ActionAddState):
    def _make_action(self):
        return PlayerAction(self._function, *self._args, **self._kwargs)
