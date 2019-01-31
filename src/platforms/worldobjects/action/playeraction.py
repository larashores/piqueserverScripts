from platforms.worldobjects.action.action import Action


class PlayerAction(Action):
    NAME = 'player'

    def run(self, players):
        for player in players:
            self._action_type.value[0](player, *self._args, **self._kwargs)

    def __str__(self):
        return 'player {}'.format(self._args)

    def serialize(self):
        return {
            'type': self.NAME,
            'action': str(self._action_type),
            'args': self._args,
            'kwargs': self._kwargs
        }
