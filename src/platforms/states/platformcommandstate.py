from platforms.states.state import State
from platforms.strings import S_COMMAND_CANCEL

S_PLATFORM_RENAMED = "Platform '{old_label}' renamed to '{label}'"
S_PLATFORM_DESTROYED = "Platform '{label}' destroyed"
S_FROZEN = "Platform '{label}' frozen"
S_UNFROZEN = "Platform '{label}' unfrozen"


class PlatformCommandState(State):
    name = 'platforms command'
    platform = None

    def __init__(self, command):
        self.command = command

    def on_exit(self, protocol, player):
        platform = self.platform
        if not platform:
            return S_COMMAND_CANCEL.format(command='platforms ' + self.command)

        command = self.command
        if command == 'name':
            old, platform.label = platform.label, self.label
            return S_PLATFORM_RENAMED.format(old_label=old, label=self.label)
        elif command == 'height':
            platform.start(self.height, 'once', 0.1, 0.0, None, force = True)
        elif command == 'freeze':
            platform.frozen = not platform.frozen
            result = S_FROZEN if platform.frozen else S_UNFROZEN
            return result.format(label = platform.label)
        elif command == 'destroy':
            platform.destroy()
            del protocol.platforms[platform.id]
            # remove actions affecting this platforms
            for button in protocol.buttons.itervalues():
                button.actions = [action for action in button.actions
                                  if getattr(action, 'platforms', None) is not platform]
            # cancel any ongoing commands targeting this platforms
            for player in protocol.players.itervalues():
                state = player.states.top()
                if not state:
                    continue
                if getattr(state.get_parent(), 'platforms', None) is platform:
                    player.states.exit()
            # clear last platforms memory from players
            for player in protocol.players.itervalues():
                if player.previous_platform is platform:
                    player.previous_platform = None
            return S_PLATFORM_DESTROYED.format(label=platform.label)
