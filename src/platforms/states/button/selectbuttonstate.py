from platforms.states.button.buttonstate import ButtonState


class SelectButtonState(ButtonState):
    button = property(lambda self: self.button)

    def __init__(self, parent_state):
        ButtonState.__init__(self)
        self._parent = parent_state
        self._button = None

    def select_button(self, button):
        self._button = button

    def on_enter(self):
        return 'Select a button by hitting it with the spade'

    def on_exit(self):
        self._parent.set_button(self.button)
        self.player.previous_button = self.button or self.player.previous_button
        if self.player.states.top() is self._parent:
            self.player.states.pop()
        elif self.button:
            return "Button '{}' selected".format(self.button.label)

    def on_select_button(self, player, button):
        if button:
            self._button = button
            self.signal_exit()
            return True
        else:
            player.send_chat('This is not a button!')
            return False
