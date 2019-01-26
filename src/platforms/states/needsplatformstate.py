class NeedsPlatformState:
    platform = property(lambda self: self._platform)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._platform = None

    def set_platform(self, platform):
        self._platform = platform
