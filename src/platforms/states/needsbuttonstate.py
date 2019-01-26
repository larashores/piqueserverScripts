class NeedsButtonState:
    button = property(lambda self: self._button)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._button = None

    def set_button(self, button):
        self._button = button
