from platform.states.state import State


class ButtonCommandState(State):
    name = 'button command'
    button = None

    def __init__(self, command):
        self.command = command

    def on_exit(self, protocol, player):
        button = self.button
        if not button:
            return S_COMMAND_CANCEL.format(command = 'button ' + self.command)

        command = self.command
        if command == 'name':
            old, button.label = button.label, self.label
            return S_BUTTON_RENAMED.format(old_label = old, label = self.label)
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
            return result.format(label = button.label)
        elif command == 'cooldown':
            button.cooldown = self.cooldown
            return S_BUTTON_COOLDOWN.format(label = button.label,
                cooldown = self.cooldown)