from platforms.states.platformsstate import PlatformsState


class ButtonState(PlatformsState):
    def on_inspect_button(self, button):
        self.player.send_chat("Button '{}', cooldown {:.2f}s".format(button.label, button.cooldown))
        return True
