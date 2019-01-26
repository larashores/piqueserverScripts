from platforms.states.platform.platformstate import PlatformState


class SelectPlatformState(PlatformState):
    platform = property(lambda self: self._platform)

    def __init__(self, parent_state):
        self.parent_state = parent_state
        self._platform = None

    def select_platform(self, platform):
        self._platform = platform

    def on_enter(self, protocol, player):
        return 'Select a platforms by hitting it with the spade'

    def on_exit(self, protocol, player):
        self.parent_state.set_platform(self.platform)
        player.previous_platform = self.platform or player.previous_platform
        if player.states.top() is self.parent_state:
            player.states.pop()
        elif self.platform:
            return "Platform '{}' selected".format(self.platform.label)
