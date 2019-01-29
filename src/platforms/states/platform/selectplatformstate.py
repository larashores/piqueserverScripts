from platforms.states.platform.platformstate import PlatformState


class SelectPlatformState(PlatformState):
    platform = property(lambda self: self._platform)

    def __init__(self, parent_state):
        PlatformState.__init__(self)
        self._parent = parent_state
        self._platform = None

    def select_platform(self, platform):
        self._platform = platform

    def on_enter(self):
        return 'Select a platform by hitting it with the spade'

    def on_exit(self):
        self._parent.set_platform(self.platform)
        self.player.previous_platform = self.platform or self.player.previous_platform
        if self.player.state_stack.top() is self._parent:
            self._parent.signal_exit(self._parent)
        elif self.platform:
            return "Platform '{}' selected".format(self.platform.label)

    def on_select_platform(self, platform):
        self._platform = platform
        self.signal_exit(self)
        return True
