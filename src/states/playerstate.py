from platforms.signal import Signal


class PlayerState:
    BLOCKING_STATE = False

    def __init__(self, parent_state=None):
        self.signal_exit = Signal()
        self.parent_state = parent_state

    def on_enter(self, protocol, player):
        pass

    def on_exit(self, protocol, player):
        pass

    def get_parent(self):
        return self.parent_state if self.parent_state else self

    def on_block_build(self, x, y, z):
        pass

    def on_line_build(self, points):
        pass

    def on_block_removed(self, x, y, z):
        pass

    def on_select_button(self, player, button):
        return False

    def on_inspect_button(self, player, button):
        return False

    def on_select_platform(self, player, platform):
        return False

    def on_inspect_platform(self, player, platform):
        return False
