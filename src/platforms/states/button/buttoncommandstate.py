from platforms.abstractattribute import abstractattribute, ABCMeta
from platforms.states.button.buttonstate import ButtonState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.strings import S_COMMAND_CANCEL


class ButtonCommandState(ButtonState, NeedsButtonState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self, protocol, player):
        if not self.button:
            return S_COMMAND_CANCEL.format(command='button {}'.format(self.COMMAND_NAME))
        self._on_activate_command(protocol, player)

    def _on_activate_command(self, protocol, player):
        pass


class ButtonNameState(ButtonCommandState):
    COMMAND_NAME = 'name'

    def __init__(self, label):
        ButtonCommandState.__init__(self)
        self.label = label

    def _on_activate_command(self, protocol, player):
        old, self.button.label = self.button.label, self.label
        return "Button '{}' renamed to '{}'".format(old, self.label)


class ButtonDestroyState(ButtonCommandState):
    COMMAND_NAME = 'destroy'

    def _on_activate_command(self, protocol, player):
        protocol.destroy_button(self.button)
        return "Button '{}' removed".format(self.button.label)


class ButtonToggleState(ButtonCommandState):
    COMMAND_NAME = 'toggle'

    def _on_activate_command(self, protocol, player):
        self.button.disabled = not self.button.disabled
        return "Button '{}' {}".format(self.button.label, 'disabled' if self.button.disabled else 'enabled')


class ButtonCooldownState(ButtonCommandState):
    COMMAND_NAME = 'cooldown'

    def __init__(self, cooldown):
        ButtonCommandState.__init__(self)
        self.cooldown = cooldown

    def _on_activate_command(self, protocol, player):
        self.button.cooldown = self.cooldown
        return "Cooldown for button '{}' set to {:.2f} seconds".format(self.button.label, self.cooldown)


class ButtonLastState(ButtonCommandState):
    COMMAND_NAME = 'last'
