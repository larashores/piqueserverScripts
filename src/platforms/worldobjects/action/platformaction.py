from platforms.worldobjects.action.action import Action, ActionType


class PlatformAction(Action):
    NAME = 'platform'

    def __init__(self, platform, action_type, *args, **kwargs):
        Action.__init__(self, action_type, *args, **kwargs)
        self._platform = platform

    def run(self, players):
        try:
            self._action_type.value[0](self._platform, *self._args, **self._kwargs)
        except:
            print(self._args, self._kwargs)
            raise

    def __str__(self):
        return 'platform {}, {}'.format(self._args, self._kwargs)

    def serialize(self):
        return {
            **Action.serialize(self),
            'platform_id': self._platform.id,
        }

    @staticmethod
    def _compatibility(action, kwargs):
        if 'mode' in kwargs:
            kwargs.pop('mode')
        if action == ActionType.LOWER or action == ActionType.RAISE:
            amount = kwargs.pop('height')
            kwargs['amount'] = amount

    @staticmethod
    def unserialize(protocol, data):
        platform = protocol.get_platform(data.pop('platform_id'))
        action = ActionType[data['action'].upper()]
        args = data['args'] if 'args' in data else []
        kwargs = data['kwargs']
        PlatformAction._compatibility(action, kwargs)
        return PlatformAction(platform, action, *args, **kwargs)
