class NeedsButtonState:
    button = property(lambda self: self._button)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._button = None

    def on_enter(self):
        return 'Select a button by hitting it with the spade'

    def select_button(self, button):
        if not self._button:
            self._button = button
            self._on_button_selected()

    def _on_button_selected(self):
        self.signal_exit(self)
