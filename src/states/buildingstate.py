from states.playerstate import PlayerState


class BuildingState(PlayerState):
    def on_block_removed(self, x, y, z):
        pass

    def on_block_build(self, x, y, z):
        pass

    def on_line_build(self, points):
        pass

    def on_line_build_attempt(self, points):
        return True

