from platforms.worldobjects.action.action import Action


class PlayerAction(Action):
    NAME = 'player'

    def __init__(self, function, *args, **kwargs):
        self._player_function = function
        self.args = args
        self.kwargs = kwargs

    def run(self, players):
        for player in players:
            self._player_function(player, *self.args, **self.kwargs)

    def serialize(self):
        return {
            'type': self.type,
            'action': self.action,
            'kwargs': self.kwargs
        }
