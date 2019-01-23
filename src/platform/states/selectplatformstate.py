from platform.states.state import State


class SelectPlatformState(State):
    name = 'select platform'
    platform = None
    parent_state = None

    def __init__(self, parent_state):
        self.parent_state = parent_state

    def on_enter(self, protocol, player):
        return S_SELECT_PLATFORM

    def on_exit(self, protocol, player):
        self.parent_state.platform = self.platform
        player.previous_platform = self.platform or player.previous_platform
        if player.states.top() is self.parent_state:
            player.states.pop()
        elif self.platform:
            return S_PLATFORM_SELECTED.format(label = self.platform.label)
