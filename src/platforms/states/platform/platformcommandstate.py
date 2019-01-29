from platforms.abstractattribute import abstractattribute, ABCMeta
from platforms.states.needsplatformstate import NeedsPlatformState
from platforms.states.platform.platformstate import PlatformState
from platforms.strings import S_COMMAND_CANCEL


class PlatformCommandState(NeedsPlatformState, PlatformState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self):
        if not self._platform:
            return S_COMMAND_CANCEL.format(command='platform {}'.format(self.COMMAND_NAME))
        return self._on_activate_command()

    def _on_activate_command(self):
        pass


class PlatformNameState(PlatformCommandState):
    COMMAND_NAME = 'name'

    def __init__(self, label):
        PlatformCommandState.__init__(self)
        self.label = label

    def _on_activate_command(self):
        old, self._platform.label = self._platform.label, self.label
        return "Platform '{}' renamed to '{}'".format(old, self.label)


class PlatformHeightState(PlatformCommandState):
    COMMAND_NAME = 'height'

    def __init__(self, height):
        PlatformCommandState.__init__(self)
        self.height = height

    def _on_activate_command(self):
        self._platform.height(self.height, .1)
        #self.platform.start(self.height, 'once', 0.1, 0.0, None, force=True)


class PlatformFreezeState(PlatformCommandState):
    COMMAND_NAME = 'freeze'

    def _on_activate_command(self):
        self._platform.frozen = not self._platform.frozen
        return "Platform {} {}".format(self._platform.label, 'frozen' if self._platform.frozen else 'unfrozen')


class PlatformDestroyState(PlatformCommandState):
    COMMAND_NAME = 'destroy'

    def _on_activate_command(self):
        self.player.protocol.destroy_platform(self._platform)
        return "Platform '{}' destroyed".format(self._platform.label)


class PlatformLastState(PlatformCommandState):
    COMMAND_NAME = 'last'
