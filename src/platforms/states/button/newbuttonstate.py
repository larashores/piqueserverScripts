from platforms.states.button.buttonstate import ButtonState


class NewButtonState(ButtonState):
    def __init__(self, label=None):
        ButtonState.__init__()
        self.label = label
        self.color = None
        self.location = None

    def on_enter(self):
        return 'Put down a block where you want the new button to be'

    def on_exit(self):
        if not self.location:
            return 'Aborting button placement'
        if not self.player.protocol.create_button(self.location, self.label, self.color):
            return 'There is already another button here!'
        return "Button '{}' created".format(self.label)

    def on_block_build(self, x, y, z):
        self.location = (x, y, z)
        self.color = self.color
        self.signal_exit()
