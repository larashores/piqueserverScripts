from platforms.states.state import State


class ButtonActionState(State):
    button = property(lambda self: self._button)

    def __init__(self):
        self._button = None

    def set_button(self, button):
        self._button = button
