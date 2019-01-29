class NeedsPlatformState:
    platform = property(lambda self: self._platform)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._platform = None

    def on_enter(self):
        return 'Select a platform by hitting it with the spade'

    def select_platform(self, platform):
        if not self._platform:
            self._platform = platform
            self._on_platform_selected()

    def _on_platform_selected(self):
        self.signal_exit(self)
