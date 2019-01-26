from platforms.states.state import State


class NeedsButtonState(State):
    platform = property(lambda self: self._platform)

    def __init__(self):
        self._platform = None

    def set_platform(self, platform):
        self._platform = platform
