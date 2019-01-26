from platforms.states.button.buttonstate import ButtonState


class SelectButtonState(ButtonState):
    button = property(lambda self: self.button)

    def __init__(self, parent_state):
        self.parent_state = parent_state
        self._button = None

    def select_button(self, button):
        self._button = button

    def on_enter(self, protocol, player):
        return 'Select a button by hitting it with the spade'

    def on_exit(self, protocol, player):
        self.parent_state.button = self.button
        player.previous_button = self.button or player.previous_button
        if player.states.top() is self.parent_state:
            player.states.pop()
        elif self.button:
            return "Button '{}' selected".format(self.button.label)
