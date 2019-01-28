from pyspades.collision import collision_3d
from platforms.commands.trigger.trigger import Trigger
from platforms.strings import *


class DistanceTrigger(Trigger):
    type = 'distance'

    def __init__(self, protocol, radius, negate=False):
        Trigger.__init__(self, protocol, negate)
        self.radius = radius

    def callback(self, player):
        player_in_range = False
        if not player.disconnected and player.world_object:
            x1, y1, z1 = parent.x + 0.5, parent.y + 0.5, parent.z + 0.5
            x2, y2, z2 = player.world_object.position.get()
            status = collision_3d(x1, y1, z1, x2, y2, z2, self.radius)
        if status:
            shared.add(player)
        else:
            shared.discard(player)
        status = bool(shared)
        if self.status != status:
            self.status = status
            self.signal_fire()

    def serialize(self):
        return {
            'type': self.type,
            'negate': self.negate,
            'radius': self.radius
        }

    def __str__(self):
        s = 'player distance={}'.format(self.radius)
        return S_TRIGGER_LIST_NOT + s if self.negate else s
