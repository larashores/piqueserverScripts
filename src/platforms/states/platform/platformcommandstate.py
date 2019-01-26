from platforms.abstractattribute import abstractattribute, abstractmethod, ABCMeta
from platforms.states.needsplatformstate import NeedsButtonState
from platforms.states.platform.platformstate import PlatformState
from platforms.strings import S_COMMAND_CANCEL


class PlatformCommandState(PlatformState, NeedsButtonState, metaclass=ABCMeta):
    COMMAND_NAME = abstractattribute

    def on_exit(self, protocol, player):
        if not self.platform:
            return S_COMMAND_CANCEL.format(command='platform {}'.format(self.COMMAND_NAME))
        self._on_activate_command(protocol, player)

    @abstractmethod
    def _on_activate_command(self, protocol, player):
        pass


class PlatformNameState(PlatformCommandState):
    COMMAND_NAME = 'name'

    def __init__(self, label):
        PlatformCommandState.__init__(self)
        self.label = label

    def _on_activate_command(self, protocol, player):
        old, self.platform.label = self.platform.label, self.label
        return "Platform '{}' renamed to '{}'".format(old, self.label)


class PlatformHeightState(PlatformCommandState):
    COMMAND_NAME = 'height'

    def __init__(self, height):
        PlatformCommandState.__init__(self)
        self.height = height

    def _on_activate_command(self, protocol, player):
        self.platform.start(self.height, 'once', 0.1, 0.0, None, force=True)


class PlatformFreezeState(PlatformCommandState):
    COMMAND_NAME = 'freeze'

    def _on_activate_command(self, protocol, player):
        self.platform.frozen = not self.platform.frozen
        return "Platform {} {}".format(self.platform.label, 'frozen' if self.platform.frozen else 'unfrozen')


class PlatformDestroyState(PlatformCommandState):
    COMMAND_NAME = 'destroy'

    def _on_activate_command(self, protocol, player):
        protocol.destroy_platorm(self.platform)
        return "Platform '{}' destroyed".format(self.platform.label)


class PlatformLastState(PlatformCommandState):
    COMMAND_NAME = 'last'
