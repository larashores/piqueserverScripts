from platforms.worldobjects.action.action import Action


class PlayerAction(Action):
    NAME = 'player'

    def __init__(self, function, *args, **kwargs):
        self._player_function = function
        self._args = args
        self._kwargs = kwargs

    def run(self, players):
        for player in players:
            self._player_function(player, *self._args, **self._kwargs)

    def __str__(self):
        return 'player {}'.format(self._args)

    def serialize(self):
        return {
            'type': self.type,
            'action': self.action,
            'kwargs': self.kwargs
        }
