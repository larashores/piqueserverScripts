from platforms.worldobjects.trigger.trigger import Trigger


class HeightTrigger(Trigger):
    NAME = 'height'

    def __init__(self, protocol, negate, platform, height):
        Trigger.__init__(self, protocol, negate)
        self._platform = platform
        self._height = height
        self._platform.add_trigger(self)

    def _status(self):
        return self._platform.height == self._height

    def update(self):
        self._fire_if_active()

    def serialize(self):
        return {
            **Trigger.serialize(self),
            'platform_id': self._platform.id,
            'height': self._height
        }

    @staticmethod
    def _unserialize(protocol, button, data):
        platform = protocol.get_platform(data['platform_id'])
        return HeightTrigger(protocol, data['negate'], platform, data['height'])

    def __str__(self):
        return "{}platform:'{}'={}".format(
            'NOT ' if self._negate else '', self._platform.label, self._height)
