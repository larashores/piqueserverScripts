from platforms.states.state import State
from platforms.strings import S_COMMAND_CANCEL

S_BUTTON_RENAMED = "Button '{old_label}' renamed to '{label}'"
S_BUTTON_DESTROYED = "Button '{label}' removed"
S_BUTTON_COOLDOWN = "Cooldown for button '{label}' set to {cooldown:.2f} seconds"
S_DISABLED = "Button '{label}' disabled"
S_ENABLED = "Button '{label}' enabled"


class ButtonCommandState(State):
    name = 'button command'
    button = None

    def __init__(self, command):
        self.command = command

    def on_exit(self, protocol, player):
        button = self.button
        if not button:
            return S_COMMAND_CANCEL.format(command='button ' + self.command)

        command = self.command
        if command == 'name':
            old, button.label = button.label, self.label
            return S_BUTTON_RENAMED.format(old_label=old, label=self.label)
        elif command == 'destroy':
            button.destroy()
            del protocol.buttons[button]
            # clear last button memory from players
            for player in protocol.players.itervalues():
                if player.previous_button is button:
                    player.previous_button = None
            return S_BUTTON_DESTROYED.format(label = button.label)
        elif command == 'toggle':
            button.disabled = not button.disabled
            result = S_DISABLED if button.disabled else S_ENABLED
            return result.format(label=button.label)
        elif command == 'cooldown':
            button.cooldown = self.cooldown
            return S_BUTTON_COOLDOWN.format(label = button.label, cooldown = self.cooldown)
