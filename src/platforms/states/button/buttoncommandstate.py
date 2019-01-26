from platforms.states.button.buttonstate import ButtonState
from platforms.states.buttonactionstate import ButtonActionState
from platforms.strings import S_COMMAND_CANCEL
from abc import abstractmethod, ABCMeta


class ButtonCommandState(ButtonState, ButtonActionState, metaclass=ABCMeta):
    def on_exit(self, protocol, player):
        if not self.button:
            return S_COMMAND_CANCEL.format(command='button name')
        self._on_activate_command(protocol, player)

    @abstractmethod
    def _on_activate_command(self, protocol, player):
        pass


class ButtonNameState(ButtonCommandState):
    def __init__(self, label):
        ButtonCommandState.__init__(self)
        self.label = label

    def _on_activate_command(self, protocol, player):
        old, self.button.label = self.button.label, self.label
        return "Button '{}' renamed to '{}'".format(old, self.label)


class ButtonDestroyState(ButtonCommandState):
    def _on_activate_command(self, protocol, player):
        protocol.destroy_button(self.button)
        return "Button '{}' removed".format(self.button.label)


class ButtonToggleState(ButtonCommandState):
    def _on_activate_command(self, protocol, player):
        self.button.disabled = not self.button.disabled
        return "Button '{}' {}".format(self.button.label, 'disabled' if self.button.disabled else 'enabled')


class ButtonCooldownState(ButtonCommandState):
    def __init__(self, cooldown):
        ButtonCommandState.__init__(self)
        self.cooldown = cooldown

    def _on_activate_command(self, protocol, player):
        self.button.cooldown = self.cooldown
        return "Cooldown for button '{}' set to {:.2f} seconds".format(self.button.label, self.cooldown)


class ButtonLastState(ButtonCommandState):
    pass
