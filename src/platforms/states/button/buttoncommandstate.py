from platforms.abstractattribute import abstractattribute, ABCMeta
from platforms.states.button.buttonstate import ButtonState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.strings import S_COMMAND_CANCEL


class ButtonCommandState(NeedsButtonState, ButtonState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self):
        if not self._button:
            return S_COMMAND_CANCEL.format(command='button {}'.format(self.COMMAND_NAME))
        return self._on_activate_command()

    def _on_activate_command(self):
        pass


class ButtonNameState(ButtonCommandState):
    COMMAND_NAME = 'name'

    def __init__(self, label):
        ButtonCommandState.__init__(self)
        self._label = label

    def _on_activate_command(self):
        old, self._button.label = self._button.label, self._label
        return "Button '{}' renamed to '{}'".format(old, self._label)


class ButtonDestroyState(ButtonCommandState):
    COMMAND_NAME = 'destroy'

    def _on_activate_command(self):
        self.player.protocol.destroy_button(self._button)
        return "Button '{}' removed".format(self._button.label)


class ButtonToggleState(ButtonCommandState):
    COMMAND_NAME = 'toggle'

    def _on_activate_command(self):
        self._button.disabled = not self._button.disabled
        return "Button '{}' {}".format(self._button.label, 'disabled' if self._button.disabled else 'enabled')


class ButtonCooldownState(ButtonCommandState):
    COMMAND_NAME = 'cooldown'

    def __init__(self, cooldown):
        ButtonCommandState.__init__(self)
        self.cooldown = cooldown

    def _on_activate_command(self):
        self._button.cooldown = self.cooldown
        return "Cooldown for button '{}' set to {:.2f} seconds".format(self._button.label, self.cooldown)
