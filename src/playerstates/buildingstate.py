class BuildingState:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_block_removed(self, x, y, z):
        pass

    def on_block_build(self, x, y, z):
        pass

    def on_line_build(self, points):
        pass

    def on_line_build_attempt(self, points):
        return True

    def on_block_destroy(self, x, y, z, mode):
        return True
