from platforms.worldobjects.action.action import Action


class PlatformAction(Action):
    NAME = 'platform'

    def __init__(self, platform, function, *args, **kwargs):
        Action.__init__(self)
        self._platform_function = function
        self._platform = platform
        self._args = args
        self._kwargs = kwargs

    def run(self, players):
        self._platform_function(self._platform, *self._args, **self._kwargs)

    def __str__(self):
        return 'platform {}'.format(self._args)

    def serialize(self):
        return {
            'type': self.type,
            'platform_id': self.platform.id,
            'action': self.action,
            'kwargs': self.kwargs
        }
