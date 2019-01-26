from pyspades.contained import BlockAction
from pyspades.constants import DESTROY_BLOCK
from platforms.states.platform.platformstate import PlatformState

import operator


class NewPlatformState(PlatformState):
    blocking = True

    def __init__(self, label=None):
        self.label = label
        self.blocks = set()

    def on_enter(self, protocol, player):
        return 'Platform construction started. Build then type /platforms when done'

    def on_exit(self, protocol, player):
        if not self.blocks:
            return 'Platform construction cancelled'

        zipped = list(zip(*self.blocks))
        x1, y1 = min(zipped[0]), min(zipped[1])
        x2, y2 = max(zipped[0]) + 1, max(zipped[1]) + 1
        z1, z2 = min(zipped[2]), max(zipped[2])
        if z1 != z2:                                    # undo placed blocks if the design is invalid
            block_action = BlockAction()
            block_action.value = DESTROY_BLOCK
            block_action.player_id = player.player_id
            for x, y, z in self.blocks:
                if protocol.map.destroy_point(x, y, z):
                    block_action.x = x
                    block_action.y = y
                    block_action.z = z
                    protocol.send_contained(block_action, save=True)
            return 'Bad platforms. Floor can be incomplete but must be flat'
        z2 += 1

        # get averaged color
        color_sum = (0, 0, 0)
        for x, y, z in self.blocks:
            color = protocol.map.get_color(x, y, z)
            color_sum = tuple(map(operator.add, color_sum, color))
        color_avg = tuple(n / len(self.blocks) for n in color_sum)

        platform = protocol.add_platform(x1, y1, z1, x2, y2, z2, color_avg, self.label)
        player.previous_platform = platform
        return "Platform '{}' created".format(platform.label)
