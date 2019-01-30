from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.states.needsplatformstate import NeedsPlatformState
from platforms.states.platform.platformstate import PlatformState
from platforms.util.strings import S_COMMAND_CANCEL


class PlatformCommandState(NeedsPlatformState, PlatformState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self):
        if not self._platform:
            return S_COMMAND_CANCEL.format(self.COMMAND_NAME)
        return self._on_activate_command()

    @abstractmethod
    def _on_activate_command(self):
        pass


class PlatformNameState(PlatformCommandState):
    COMMAND_NAME = 'platform name'

    def __init__(self, label):
        PlatformCommandState.__init__(self)
        self._label = label

    def _on_activate_command(self):
        old, self._platform.label = self._platform.label, self._label
        return "Platform '{}' renamed to '{}'".format(old, self._label)


class PlatformHeightState(PlatformCommandState):
    COMMAND_NAME = 'height'

    def __init__(self, height):
        PlatformCommandState.__init__(self)
        self._height = height

    def _on_activate_command(self):
        self._platform.set_height(self._height, .1)


class PlatformFreezeState(PlatformCommandState):
    COMMAND_NAME = 'platform freeze'

    def _on_activate_command(self):
        self._platform.frozen = not self._platform.frozen
        return "Platform {} {}".format(self._platform.label, 'frozen' if self._platform.frozen else 'unfrozen')


class PlatformDestroyState(PlatformCommandState):
    COMMAND_NAME = 'platform destroy'

    def _on_activate_command(self):
        self.player.protocol.destroy_platform(self._platform)
        return "Platform '{}' destroyed".format(self._platform.label)
