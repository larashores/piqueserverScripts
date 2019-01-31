from platforms.worldobjects.trigger.playertrigger import PlayerTrigger


class PressTrigger(PlayerTrigger):
    ONE_PER_BUTTON = True
    NAME = 'press'

    def update(self, player):
        self.affected_players.add(player)
        self._fire_if_active()
        self.affected_players.discard(player)

    def serialize(self):
        return {
            'type': PressTrigger.NAME,
            'negate': self._negate,
        }

    def __str__(self):
        return "{}press".format('NOT ' if self._negate else '')
