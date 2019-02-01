from platforms.worldobjects.action.action import Action, ActionType


class PlayerAction(Action):
    NAME = 'player'

    def run(self, players):
        for player in players:
            self._action_type.value[0](player, *self._args, **self._kwargs)

    def __str__(self):
        return 'player {}'.format(self._args)

    @staticmethod
    def unserialize(protocol, data):
        action = ActionType[data['action'].upper()]
        args = data['args'] if 'args' in data else []
        kwargs = data['kwargs']
        return PlayerAction(action, *args, **kwargs)
