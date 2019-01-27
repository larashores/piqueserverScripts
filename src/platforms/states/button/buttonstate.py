from playerstates.playerstate import PlayerState


class ButtonState(PlayerState):
    def on_inspect_button(self, player, button):
        player.send_chat("Button '{}', cooldown {:.2f}s".format(button.label, button.cooldown))
        return True
