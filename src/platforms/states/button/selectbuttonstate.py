from platforms.states.button.buttonstate import ButtonState
from playerstates.buildingstate import BuildingState


class SelectButtonState(BuildingState, ButtonState):
    button = property(lambda self: self._button)

    def __init__(self, parent_state):
        super().__init__()
        self._parent = parent_state
        self._button = None

    def select_button(self, button):
        self._button = button

    def on_enter(self):
        return 'Select a button by hitting it with the spade'

    def on_exit(self):
        self._parent.set_button(self._button)
        self.player.last_button = self._button or self.player.last_button
        if self.player.state_stack.top() is self._parent:
            self._parent.signal_exit(self._parent)
        elif self._button:
            return "Button '{}' selected".format(self._button.label)

    def on_select_button(self, button):
        self._button = button
        self.signal_exit(self)
        return True
