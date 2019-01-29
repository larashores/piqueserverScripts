from playerstates.playerstate import PlayerState


class PlatformsState(PlayerState):
    def on_inspect_button(self, button):
        return False

    def on_inspect_platform(self, platform):
        return False
