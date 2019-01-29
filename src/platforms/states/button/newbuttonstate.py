from platforms.states.button.buttonstate import ButtonState
from playerstates.buildingstate import BuildingState


class NewButtonState(BuildingState, ButtonState):
    def __init__(self, label=None):
        super().__init__()
        self._label = label
        self._color = None
        self._location = None

    def on_enter(self):
        return 'Put down a block where you want the new button to be'

    def on_exit(self):
        if not self._location:
            return 'Aborting button placement'
        button = self.player.protocol.create_button(self._location, self._color, self._label)
        if not button:
            return 'There is already another button or platform here!'
        self.player.last_button = button
        return "Button '{}' created".format(button.label)

    def on_block_build(self, x, y, z):
        self._location = (x, y, z)
        self._color = self.player.color
        self.signal_exit(self)
