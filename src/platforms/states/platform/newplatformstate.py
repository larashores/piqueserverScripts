from pyspades.contained import BlockAction
from pyspades.constants import DESTROY_BLOCK
from platforms.states.platform.platformstate import PlatformState
from playerstates.buildingstate import BuildingState

import operator


class NewPlatformState(BuildingState, PlatformState):
    blocking = True

    def __init__(self, label=None):
        super().__init__()
        self.label = label
        self.blocks = set()

    def on_enter(self):
        return 'Platform construction started. Build then type /platforms when done'

    def on_exit(self):
        if not self.blocks:
            return 'Platform construction cancelled'

        zipped = list(zip(*self.blocks))
        x1, y1 = min(zipped[0]), min(zipped[1])
        x2, y2 = max(zipped[0]) + 1, max(zipped[1]) + 1
        z1, z2 = min(zipped[2]), max(zipped[2])
        if z1 != z2:                                    # undo placed blocks if the design is invalid
            block_action = BlockAction()
            block_action.value = DESTROY_BLOCK
            block_action.player_id = self.player.player_id
            for x, y, z in self.blocks:
                if self.player.protocol.map.destroy_point(x, y, z):
                    block_action.x = x
                    block_action.y = y
                    block_action.z = z
                    self.player.protocol.send_contained(block_action, save=True)
            return 'Bad platforms. Floor can be incomplete but must be flat'
        z2 += 1

        # get averaged color
        color_sum = (0, 0, 0)
        for x, y, z in self.blocks:
            color = self.player.protocol.map.get_color(x, y, z)
            color_sum = tuple(map(operator.add, color_sum, color))
        color_avg = tuple(n / len(self.blocks) for n in color_sum)

        platform = self.player.protocol.add_platform(x1, y1, z1, x2, y2, z2, color_avg, self.label)
        self.player.previous_platform = platform
        return "Platform '{}' created".format(platform.label)

    def on_block_build(self, x, y, z):
        self.blocks.add((x, y, z))

    def on_line_build(self, points):
        self.blocks.update(points)

    def on_block_removed(self, x, y, z):
        self.blocks.discard((x, y, z))
