PLATFORM_ACTION_FUNCTIONS = {
    'start': 'start',
    'height': 'start',
    'raise': 'start',
    'lower': 'start',
    'elevator': 'start',
    'output': 'start'
}


class PlatformAction:
    type = 'platform'

    def __init__(self, protocol, platform_id, action, kwargs):
        self.platform = protocol.platforms[platform_id]
        self.action = action
        func_name = PLATFORM_ACTION_FUNCTIONS[action]
        self.callback = getattr(self.platform, func_name)
        self.kwargs = kwargs

    def run(self, value, objects):
        if self.action == 'output':
            self.callback(height=int(value), **self.kwargs)
        elif value:
            self.callback(**self.kwargs)

    def serialize(self):
        return {
            'type': self.type,
            'platform_id': self.platform.id,
            'action': self.action,
            'kwargs': self.kwargs
        }

    def __str__(self):
        return "platform '{}' {}({})" .format(self.platform.label, self.kwargs['mode'], self.kwargs['height'])
