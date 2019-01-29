from platforms.worldobjects.trigger.trigger import Trigger
from abc import ABCMeta


class PlayerTrigger(Trigger, metaclass=ABCMeta):
    ONE_PER_BUTTON = True

    def __init__(self, protocol, negate=False):
        Trigger.__init__(self, protocol, negate)
        self.affected_players = set()

    def _status(self):
        return len(self.affected_players) != 0
