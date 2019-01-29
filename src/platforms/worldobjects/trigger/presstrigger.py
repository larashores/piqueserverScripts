from platforms.worldobjects.trigger.playertrigger import PlayerTrigger


class PressTrigger(PlayerTrigger):
    NAME = 'press'

    def update(self, player):
        self.affected_players.add(player)
        self.signal_fire()
        self.affected_players.discard(player)

    def __str__(self):
        return "{}player press".format('NOT ' if self._negate else '')
