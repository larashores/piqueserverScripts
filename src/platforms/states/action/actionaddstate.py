from platforms.abstractattribute import abstractmethod, ABCMeta
from platforms.worldobjects.action.platformaction import PlatformAction
from platforms.worldobjects.action.playeraction import PlayerAction
from platforms.states.buttonactionstate import ButtonActionState
from platforms.strings import *


class ActionAddState(ButtonActionState, metaclass=ABCMeta):
    def __init__(self, action_type, clear_others=True, **kwargs):
        ButtonActionState.__init__(self)
        self.action_type = action_type
        self.clear_others = clear_others
        self.platform = None
        self.kwargs = kwargs

    def on_exit(self, protocol, player):
        if not self.button:
            return S_COMMAND_CANCEL.format(command='action')
        action = self._make_action(protocol)
        if action is None:
            return S_COMMAND_CANCEL.format(command='action {}'.format(self.action_type.name.lower()))

        if not self.clear_others:
            self.button.actions.clear()
        self.button.actions.append(action)
        return "Added {} action to button '{}'".format(self.action_type.value, self.button.label)

    @abstractmethod
    def _make_action(self, protocol):
        pass


class PlatformActionAddState(ActionAddState, metaclass=ABCMeta):
    def _make_action(self, protocol):
        return PlatformAction(protocol, self.platform.id, self.action_type, self.kwargs) if self.platform else None


class PlayerActionAddState(ActionAddState, metaclass=ABCMeta):
    def _make_action(self, protocol):
        return PlayerAction(protocol, self.action_type, self.kwargs)
