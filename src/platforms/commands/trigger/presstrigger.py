from platforms.commands.trigger.trigger import Trigger
from platforms.strings import *


class PressTrigger(Trigger):
    type = 'press'
    unique = True

    def callback(self, player):
        shared = self.parent.shared_trigger_objects[self.type]
        shared.add(player)
        self.status = True
        self.parent.trigger_check()
        self.status = False
        shared.discard(player)

    def __str__(self):
        s = 'player press'
        return S_TRIGGER_LIST_NOT + s if self.negate else s
