from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.states.needsplatformstate import NeedsPlatformState


class NeedsBothState(NeedsPlatformState, NeedsButtonState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_enter(self):
        self.player.send_chat(NeedsButtonState.on_enter(self))
        self.player.send_chat(NeedsPlatformState.on_enter(self))

    def _on_button_selected(self):
        if self._platform:
            NeedsButtonState._on_button_selected(self)
        else:
            self.player.send_chat("Button '{}' selected".format(self._button.label))

    def _on_platform_selected(self):
        if self._button:
            NeedsPlatformState._on_platform_selected(self)
        else:
            self.player.send_chat("Platform '{}' selected".format(self._platform.label))
