from playerstates.buildingstate import BuildingState


class ButtonState(BuildingState):
    def on_inspect_button(self, player, button):
        player.send_chat("Button '{}', cooldown {:.2f}s".format(button.label, button.cooldown))
        return True
