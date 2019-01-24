from platforms.states.state import State
from platforms.commands.trigger.presstrigger import PressTrigger
from platforms.worldobjects.button import Button

S_BUTTON_PLACEMENT = 'Put down a block where you want the new button to be'
S_BUTTON_CREATED = "Button '{label}' created"
S_BUTTON_CANCEL = 'Aborting button placement'
S_BUTTON_OVERLAPS = 'There is already another button here!'


class NewButtonState(State):
    name = 'new button'
    location = None
    label = None

    def __init__(self, label=None):
        self.label = label

    def on_enter(self, protocol, player):
        return S_BUTTON_PLACEMENT

    def on_exit(self, protocol, player):
        if not self.location:
            return S_BUTTON_CANCEL
        if self.location in protocol.buttons:
            return S_BUTTON_OVERLAPS

        protocol.highest_id += 1
        id = protocol.highest_id
        x, y, z = self.location
        button = Button(protocol, id, x, y, z, self.color)
        button.label = self.label or button.label
        button.add_trigger(PressTrigger(protocol))
        protocol.buttons[(id, (x, y, z))] = button
        player.previous_button = button
        return S_BUTTON_CREATED.format(label=button.label)
