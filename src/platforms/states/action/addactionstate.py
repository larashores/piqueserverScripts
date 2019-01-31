from platforms.util.abstractattribute import abstractmethod, ABCMeta
from platforms.worldobjects.action.platformaction import PlatformAction
from platforms.worldobjects.action.playeraction import PlayerAction
from platforms.worldobjects.platform import Platform
from platforms.states.action.actionstate import ActionState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.states.needsbothstate import NeedsBothState
from platforms.util.strings import *
from piqueserver.player import FeatureConnection

import enum


#  The must be in a list or else enum will count them as functions not enumerations
class ActionType(enum.Enum):
    HEIGHT = [Platform.set_height]
    RAISE = [Platform.raise_]
    LOWER = [Platform.lower]
    ELEVATOR = [Platform.set_height]
    CHAT = [FeatureConnection.send_chat]
    TELEPORT = [FeatureConnection.set_location]
    DAMAGE = [FeatureConnection.hit]

    def __str__(self):
        return self.name.lower()


class _AddActionState(NeedsButtonState, ActionState, metaclass=ABCMeta):
    def __init__(self, clear_others, action_type, *args, **kwargs):
        super().__init__()
        self._action_type = action_type
        self._clear_others = clear_others
        self._args = args
        self._kwargs = kwargs

    def on_exit(self):
        if not self._button:
            return S_COMMAND_CANCEL.format(command='action {}'.format(self._action_type))

        if self._clear_others:
            self._button.clear_actions()
        self._button.add_action(self._make_action())
        return "Added {} action to button '{}'".format(self._action_type, self._button.label)

    @abstractmethod
    def _make_action(self):
        pass


class PlatformAddActionState(NeedsBothState, _AddActionState):
    def on_exit(self):
        if not self._platform:
            return S_COMMAND_CANCEL.format(command='action {} '.format(self._action_type))
        return _AddActionState.on_exit(self)

    def _make_action(self):
        action = PlatformAction(self._platform, self._action_type.value[0], *self._args, **self._kwargs)
        self._platform.add_action(action)
        return action


class PlayerAddActionState(_AddActionState):
    def _make_action(self):
        return PlayerAction(self._action_type.value[0], *self._args, **self._kwargs)
