from platforms.worldobjects.action.action import Action


class PlatformAction(Action):
    NAME = 'platform'

    def __init__(self, platform, action_type, *args, **kwargs):
        Action.__init__(self, action_type, *args, **kwargs)
        self._platform = platform

    def run(self, players):
        self._action_type.value[0](self._platform, *self._args, **self._kwargs)

    def __str__(self):
        return 'platform {}'.format(self._args)

    def serialize(self):
        return {
            'type': self.NAME,
            'action': str(self._action_type),
            'platform_id': self._platform.id,
            'args': self._args,
            'kwargs': self._kwargs
        }
