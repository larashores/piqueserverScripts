from platform.strings import S_NICE_LOCATION

PLAYER_ACTION_FUNCTIONS = {
    'teleport': 'set_location',
    'chat': 'send_chat',
    'damage': 'hit'
}


class PlayerAction:
    type = 'player'

    def __init__(self, protocol, action, kwargs):
        self.action = action
        func_name = PLAYER_ACTION_FUNCTIONS[action]
        self.callback = getattr(protocol.connection_class, func_name)
        self.kwargs = kwargs

    def run(self, value, objects):
        if not value:
            return
        for player in objects:
            self.callback(player, **self.kwargs)

    def serialize(self):
        return {
            'type' : self.type,
            'action' : self.action,
            'kwargs' : self.kwargs
        }

    def __str__(self):
        if self.action == 'teleport':
            info = S_NICE_LOCATION.format(*self.kwargs['location'])
        elif self.action == 'chat':
            info = '"{}"'.format(self.kwargs['value'].strip())
        elif self.action == 'damage':
            info = self.kwargs['value']
        return "player {}({})".format(self.action, info)
