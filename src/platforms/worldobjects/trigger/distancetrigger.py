from pyspades.collision import collision_3d
from platforms.commands.trigger.trigger import Trigger
from platforms.strings import *


class DistanceTrigger(Trigger):
    type = 'distance'

    def __init__(self, protocol, radius, negate = False):
        Trigger.__init__(self, protocol, negate)
        self.radius = radius
        protocol.position_triggers.append(self)

    def unbind(self):
        Trigger.unbind(self)
        shared = self.parent.shared_trigger_objects[self.type]
        shared.clear()
        self.protocol.position_triggers.remove(self)

    def callback(self, player):
        parent = self.parent
        if not parent:
            return
        shared = parent.shared_trigger_objects[self.type]
        status = False
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
            if self.parent:
                parent.trigger_check()

    def serialize(self):
        return {
            'type': self.type,
            'negate': self.negate,
            'radius': self.radius
        }

    def __str__(self):
        s = 'player distance={}'.format(self.radius)
        return S_TRIGGER_LIST_NOT + s if self.negate else s
