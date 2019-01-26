from twisted.internet.reactor import callLater, seconds
from pyspades.constants import SPADE_TOOL, GRENADE_DESTROY, DESTROY_BLOCK, SPADE_DESTROY
from platforms.states.statestack import StateStack
from platforms.states.platform.platformstate import PlatformState
from platforms.states.platform.selectplatformstate import SelectPlatformState
from platforms.states.button.buttonstate import ButtonState
from platforms.states.button.selectbuttonstate import SelectButtonState
from platforms.util.geometry import prism_range

ACTION_RAY_LENGTH = 8.0
ACTION_RAY_LENGTH_LONG = 32.0
ACTION_COOLDOWN = 0.25

S_PLATFORM_INFO = "Platform '{label}', height {height}"
S_NOT_A_PLATFORM = 'This is not a platform!'
S_NOT_A_BUTTON = 'This is not a button!'
S_BUTTON_INFO = "Button '{label}', cooldown {cooldown:.2f}s"


def platform_connection(connection):
    class PlatformConnection(connection):
        states = None
        where_location = None
        where_orientation = None
        last_action = None
        previous_button = None
        previous_platform = None
        reach = ACTION_RAY_LENGTH

        def on_reset(self):
            if self.states:
                self.states.stack = []
            self.where_location = None
            self.where_orientation = None
            self.last_action = None
            self.previous_button = None
            self.previous_platform = None
            connection.on_reset(self)

        def on_login(self, name):
            self.states = StateStack(self)
            connection.on_login(self, name)

        def on_disconnect(self):
            self.states = None
            for trigger in self.protocol.position_triggers:
                trigger.callback(self)
            connection.on_disconnect(self)

        def on_block_build(self, x, y, z):
            state = self.states.top()
            if state:
                if state.name == 'new platforms':
                    state.blocks.add((x, y, z))
                elif state.name == 'new button':
                    state.location = (x, y, z)
                    state.color = self.color
                    self.states.pop()
            connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            state = self.states.top()
            if state and state.name == 'new platforms':
                state.blocks.update(points)
            connection.on_line_build(self, points)

        def on_block_destroy(self, x, y, z, mode):
            is_platform = self.protocol.is_platform
            if mode == DESTROY_BLOCK and is_platform(x, y, z):
                return False
            elif mode == SPADE_DESTROY:
                if is_platform(x, y, z) or is_platform(x, y, z + 1) or is_platform(x, y, z - 1):
                    return False
            elif mode == GRENADE_DESTROY:
                if any(map(is_platform, *(zip(*prism_range(x - 1, y - 1, z - 1, x + 2, y + 2, z + 2))))):
                    return False
                for i, j, k in prism_range(x - 1, y - 1, z - 1, x + 2, y + 2, z + 2):
                    if is_platform(i, j, k):
                        return False
            return connection.on_block_destroy(self, x, y, z, mode)

        def on_block_removed(self, x, y, z):
            state = self.states.top()
            if state and state.name == 'new platforms':
                state.blocks.discard((x, y, z))
            connection.on_block_removed(self, x, y, z)

        def on_shoot_set(self, fire):
            if self.tool == SPADE_TOOL and fire:
                player_action(self, True, False)
            connection.on_shoot_set(self, fire)

        def on_position_update(self):
            if self.tool == SPADE_TOOL:
                player_action(self, self.world_object.primary_fire, False)
            return connection.on_position_update(self)      # wasn't originally returning?

        def on_orientation_update(self, x, y, z):
            if self.tool == SPADE_TOOL:
                player_action(self, self.world_object.primary_fire, False)
            return connection.on_orientation_update(self, x, y, z)

        def on_animation_update(self, jump, crouch, sneak, sprint):
            if self.tool == SPADE_TOOL:
                inspect = not self.world_object.sneak and sneak
                player_action(self, self.world_object.primary_fire, inspect)
            return connection.on_animation_update(self, jump, crouch, sneak, sprint)

        def on_command(self, command, parameters):
            if command == 'where' and not parameters:
                self.where_location = self.world_object.position.get()
                self.where_orientation = self.world_object.orientation.get()
            connection.on_command(self, command, parameters)

        def _get_button_if_within_reach(self):
            location = self.world_object.cast_ray(self.reach)
            if location is None:
                return None
            return self.protocol.buttons.get(location)

        def _get_platform_if_within_reach(self):
            location = self.world_object.cast_ray(self.reach)
            if location is None:
                return None
            return self.protocol.get_platform(*location)

        def _player_action(self, spade_selecting, inspect):
            if not spade_selecting and not inspect:
                return
            protocol = self.protocol
            if not protocol.platforms and not protocol.buttons:
                return
            state = self.states.top()
            if inspect and not state and not spade_selecting:
                return
            last_action = self.last_action
            if last_action is not None and seconds() - last_action <= ACTION_COOLDOWN:
                return
            self.last_action = seconds()
            button = self._get_platform_if_within_reach()
            if button:
                if isinstance(state, ButtonState):
                    if spade_selecting and isinstance(state, SelectButtonState):
                        state.select_button(button)
                        self.states.pop()
                        return
                    else:
                        self.send_chat(S_NOT_A_BUTTON)
                    info = S_BUTTON_INFO.format(label=button.label, cooldown=button.cooldown)
                    self.send_chat(info)
                    return
                if not inspect:
                    for trigger in button.triggers:
                        if trigger.type == 'press':
                            trigger.callback(self)
            elif state and isinstance(state, PlatformState):
                platform = self._get_platform_if_within_reach()
                if spade_selecting and isinstance(state, SelectPlatformState):
                    if platform:
                        state.platform = platform
                        self.states.pop()
                        return
                    else:
                        self.send_chat(S_NOT_A_PLATFORM)
                elif inspect:
                    info = S_PLATFORM_INFO.format(label=platform.label, height=platform.height)
                    self.send_chat(info)

    return PlatformConnection
