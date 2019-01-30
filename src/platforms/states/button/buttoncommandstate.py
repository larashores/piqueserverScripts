from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.states.button.buttonstate import ButtonState
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.util.strings import S_COMMAND_CANCEL


class _ButtonCommandState(NeedsButtonState, ButtonState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self):
        if not self._button:
            return S_COMMAND_CANCEL.format(command=self.COMMAND_NAME)
        return self._on_activate_command()

    @abstractmethod
    def _on_activate_command(self):
        pass


class ButtonNameState(_ButtonCommandState):
    COMMAND_NAME = 'button name'

    def __init__(self, label):
        _ButtonCommandState.__init__(self)
        self._label = label

    def _on_activate_command(self):
        old, self._button.label = self._button.label, self._label
        return "Button '{}' renamed to '{}'".format(old, self._label)


class ButtonDestroyState(_ButtonCommandState):
    COMMAND_NAME = 'button destroy'

    def _on_activate_command(self):
        self.player.protocol.destroy_button(self._button)
        return "Button '{}' removed".format(self._button.label)


class ButtonToggleState(_ButtonCommandState):
    COMMAND_NAME = 'button toggle'

    def _on_activate_command(self):
        self._button.disabled = not self._button.disabled
        return "Button '{}' {}".format(self._button.label, 'disabled' if self._button.disabled else 'enabled')


class ButtonCooldownState(_ButtonCommandState):
    COMMAND_NAME = 'button cooldown'

    def __init__(self, cooldown):
        _ButtonCommandState.__init__(self)
        self._cooldown = cooldown

    def _on_activate_command(self):
        self._button.cooldown = self._cooldown
        return "Cooldown for button '{}' set to {:.2f} seconds".format(self._button.label, self._cooldown)


class ButtonQuietState(_ButtonCommandState):
    COMMAND_NAME = 'button quiet'

    def _on_activate_command(self):
        self._button.silent = not self._button.silent
        return "Button {} will {}".format(
            self._button.label, 'activate quietly' if self._button.silent else 'animate when activated')
