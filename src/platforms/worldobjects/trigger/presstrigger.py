from platforms.worldobjects.trigger.playertrigger import PlayerTrigger


class PressTrigger(PlayerTrigger):
    ONE_PER_BUTTON = True
    NAME = 'press'

    def update(self, player):
        self.affected_players.add(player)
        self._fire_if_active()
        self.affected_players.discard(player)

    def __str__(self):
        return "{}press".format('NOT ' if self._negate else '')

    @staticmethod
    def _unserialize(protocol, button, data):
        return PressTrigger(protocol, data['negate'], button)
