from pyspades.collision import collision_3d
from platforms.worldobjects.trigger.playertrigger import PlayerTrigger


class DistanceTrigger(PlayerTrigger):
    NAME = 'distance'

    def __init__(self, protocol, negate, button, radius):
        PlayerTrigger.__init__(self, protocol, negate, button)
        self._radius = radius
        self._protocol.add_distance_trigger(self)

    def unbind(self):
        self._protocol.remove_distance_trigger(self)

    def update(self, player):
        if not player.world_object:
            return
        location1 = [coord + 0.5 for coord in self._button.location]
        location2 = player.world_object.position.get()
        if collision_3d(*location1, *location2, self._radius):
            if player not in self.affected_players:
                self.affected_players.add(player)
                self._fire_if_active()
        else:
            if player in self.affected_players:
                self.affected_players.remove(player)
                self._fire_if_active()

    def serialize(self):
        return {
            'type': self.type,
            'negate': self._negate,
            'radius': self._radius
        }

    def __str__(self):
        return '{}distance={}'.format('NOT ' if self._negate else '', self._radius)
