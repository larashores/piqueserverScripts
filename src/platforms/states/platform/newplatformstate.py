from pyspades.contained import BlockAction
from pyspades.constants import DESTROY_BLOCK
from platforms.states.platform.platformstate import PlatformState
from playerstates.buildingstate import BuildingState

import operator


class NewPlatformState(BuildingState, PlatformState):
    BLOCKING = True

    def __init__(self, label=None):
        super().__init__()
        self._label = label
        self._blocks = set()

    def on_enter(self):
        return 'Platform construction started. Build then type /platform when done'

    def on_exit(self):
        if not self._blocks:
            return 'Platform construction cancelled'

        xs, ys, zs = list(zip(*self._blocks))
        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)
        z1, z2 = min(zs), max(zs)
        if z1 != z2:                                    # undo placed blocks if the design is invalid
            block_action = BlockAction()
            block_action.value = DESTROY_BLOCK
            block_action.player_id = self.player.player_id
            for x, y, z in self._blocks:
                if self.player.protocol.map.destroy_point(x, y, z):
                    block_action.x = x
                    block_action.y = y
                    block_action.z = z
                    self.player.protocol.send_contained(block_action, save=True)
            return 'Bad platforms. Floor can be incomplete but must be flat'

        # get averaged color
        color_sum = (0, 0, 0)
        for x, y, z in self._blocks:
            color = self.player.protocol.map.get_color(x, y, z)
            color_sum = tuple(map(operator.add, color_sum, color))
        color_avg = tuple(int(n / len(self._blocks)) for n in color_sum)

        platform = self.player.protocol.create_platform((x1, y1), (x2, y2), z1, color_avg, self._label)
        if not platform:
            return 'There is already another button or platform here!'
        self.player.previous_platform = platform
        return "Platform '{}' created".format(platform.label)

    def on_block_build(self, x, y, z):
        self._blocks.add((x, y, z))

    def on_line_build(self, points):
        self._blocks.update(points)

    def on_block_removed(self, x, y, z):
        self._blocks.discard((x, y, z))
