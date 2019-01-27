from platforms.states.state import State


class PlatformState(State):
    def on_inspect_platform(self, player, platform):
        player.send_chat("Platform '{}', height {}".format(platform.label, platform.height))
        return True
