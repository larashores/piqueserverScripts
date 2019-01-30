from pyspades.collision import collision_3d
from platforms.worldobjects.trigger.trigger import Trigger


class TrackTrigger(Trigger):
    type = 'track'
    tracked_player = None

    # def __init__(self, protocol, button, radius, negate=False):
    #     Trigger.__init__(self, protocol, negate)
    #     self.radius = radius
    #
    # def callback(self, player):
    #     if not parent:
    #         return
    #     shared = parent.shared_trigger_objects[self.type]
    #     if self.status:
    #         if self.tracked_player is not player:
    #             # we're already locked on a different player
    #             return
    #     elif player in shared:
    #         # another trigger has already claimed this player
    #         return
    #     status = False
    #     if not player.disconnected and player.world_object:
    #         x1, y1, z1 = parent.x + 0.5, parent.y + 0.5, parent.z + 0.5
    #         x2, y2, z2 = player.world_object.position.get()
    #         status = collision_3d(x1, y1, z1, x2, y2, z2, self.radius)
    #     if self.status != status:
    #         # keep track of the player to avoid tripping other distance triggers
    #         # in the same button
    #         if status:
    #             shared.add(player)
    #             self.tracked_player = player
    #         else:
    #             shared.discard(player)
    #             self.tracked_player = None
    #
    #         self.status = status
    #         self.signal_fire()
    #
    # def serialize(self):
    #     return {
    #         'type': self.type,
    #         'negate': self.negate,
    #         'radius': self.radius
    #     }
    #
    # def __str__(self):
    #     return 'track distance={}'.format('NOT ' if self._negate else '', self.radius)
