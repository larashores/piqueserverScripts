from platforms.strings import S_NICE_LOCATION
import enum


class PlayerActionType(enum.Enum):
    TELEPORT = 0
    CHAT = 1
    DAMAGE = 2


PLAYER_ACTION_FUNCTIONS = {
    'teleport': 'set_location',
    'chat': 'send_chat',
    'damage': 'hit'
}


class PlayerAction:
    type = 'player'

    def __init__(self, protocol, function, *args, **kwargs):
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
