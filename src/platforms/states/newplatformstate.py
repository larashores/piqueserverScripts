from pyspades.contained import BlockAction
from pyspades.constants import DESTROY_BLOCK
from platforms.states.state import State
from platforms.worldobjects.platform import Platform

import operator

S_PLATFORM_STARTED = 'Platform construction started. Build then type /platforms when done'
S_PLATFORM_NOT_FLAT = 'Bad platforms. Floor can be incomplete but must be flat'
S_PLATFORM_CREATED = "Platform '{label}' created"
S_PLATFORM_CANCEL = 'Platform construction cancelled'


class NewPlatformState(State):
    name = 'new platforms'
    blocking = True
    label = None

    def __init__(self, label = None):
        self.label = label

    def on_enter(self, protocol, player):
        self.blocks = set()
        return S_PLATFORM_STARTED

    def on_exit(self, protocol, player):
        if not self.blocks:
            return S_PLATFORM_CANCEL

        zipped = zip(*self.blocks)
        x1, y1 = min(zipped[0]), min(zipped[1])
        x2, y2 = max(zipped[0]) + 1, max(zipped[1]) + 1
        z1, z2 = min(zipped[2]), max(zipped[2])
        if z1 != z2:
            # undo placed blocks if the design is invalid
            block_action = BlockAction()
            block_action.value = DESTROY_BLOCK
            block_action.player_id = player.player_id
            for x, y, z in self.blocks:
                if protocol.map.destroy_point(x, y, z):
                    block_action.x = x
                    block_action.y = y
                    block_action.z = z
                    protocol.send_contained(block_action, save = True)
            return S_PLATFORM_NOT_FLAT
        z2 += 1

        # get averaged color
        color_sum = (0, 0, 0)
        for x, y, z in self.blocks:
            color = protocol.map.get_color(x, y, z)
            color_sum = tuple(map(operator.add, color_sum, color))
        color_avg = tuple(n / len(self.blocks) for n in color_sum)

        protocol.highest_id += 1
        id = protocol.highest_id
        platform = Platform(protocol, id, x1, y1, z1, x2, y2, z2, color_avg)
        platform.label = self.label or platform.label
        platform.build_plane(z1)
        protocol.platforms[id] = platform
        player.previous_platform = platform
        return S_PLATFORM_CREATED.format(label = platform.label)
