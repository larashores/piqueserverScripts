from platforms.worldobjects.trigger.trigger import Trigger
from platforms.strings import *


class PressTrigger(Trigger):
    NAME = 'press'
    ONE_PER_BUTTON = True

    def callback(self, player):
        self.affected_players.add(player)
        self._status = True
        self.signal_fire()
        self._status = False
        self.affected_players.clear()

    def __str__(self):
        return "{}player press".format('NOT ' if self.negate else s)
