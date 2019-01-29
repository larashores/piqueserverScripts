from platforms.states.platformsstate import PlatformsState


class PlatformState(PlatformsState):
    def on_inspect_platform(self, platform):
        self.player.send_chat("Platform '{}', height {}".format(platform.label, platform.height))
        return True
