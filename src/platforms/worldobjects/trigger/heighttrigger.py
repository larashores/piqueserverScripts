from platforms.worldobjects.trigger.trigger import Trigger


class HeightTrigger(Trigger):
    type = 'height'

    def __init__(self, protocol, button, platform_id, height, negate=False):
        Trigger.__init__(self, protocol, button, negate)
        platform = protocol.platforms[platform_id]
        self.platform = platform
        self.target_height = height
        if platform.bound_triggers is None:
            platform.bound_triggers = []
        platform.bound_triggers.append(self)
        self.callback(platform)

    def unbind(self):
        Trigger.unbind(self)
        self.platform.bound_triggers.remove(self)

    def callback(self, platform):
        met = platform.height == self.target_height
        if self.status != met:
            self.status = met
            self.signal_fire()

    def serialize(self):
        return {
            'type': self.type,
            'negate': self.negate,
            'platform_id': self.platform.id,
            'height': self.target_height
        }

    def __str__(self):
        return "{}platforms '{}' height={}".format(
            'NOT ' if self._negate else '', self.platform.label, self.target_height)
