from twisted.internet.reactor import seconds
from pyspades.constants import SPADE_TOOL, GRENADE_DESTROY, DESTROY_BLOCK, SPADE_DESTROY
from platforms.states.needsbuttonstate import NeedsButtonState
from platforms.states.needsplatformstate import NeedsPlatformState
from platforms.util.geometry import prism_range
from playerstates.stateconnection import state_connection

ACTION_RAY_LENGTH = 8.0
ACTION_COOLDOWN = 0.25


def platform_connection(connection):
    connection = state_connection(connection)

    class PlatformConnection(connection):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.last_button = None
            self.last_platform = None
            self.where_location = None
            self.where_orientation = None
            self._last_action = 0

        def on_block_destroy(self, x, y, z, mode):
            if mode == DESTROY_BLOCK:
                affected_blocks = [(x, y, z)]
            elif mode == SPADE_DESTROY:
                affected_blocks = [(x, y, z), (x, y, z + 1), (x, y, z - 1)]
            elif mode == GRENADE_DESTROY:
                affected_blocks = prism_range(x - 1, y - 1, z - 1, x + 2, y + 2, z + 2)
            else:
                affected_blocks = []
            for location in affected_blocks:
                if self.protocol.is_platform_or_button(location):
                    return False
            return connection.on_block_destroy(self, x, y, z, mode)

        def on_shoot_set(self, fire):
            if self.tool == SPADE_TOOL and fire:
                state = self.state_stack.top()
                button, platform = self._get_button_or_platform_if_within_reach()
                if button and isinstance(state, NeedsButtonState):
                    state.select_button(button)
                elif platform and isinstance(state, NeedsPlatformState):
                    state.select_platform(platform)
                elif button and seconds() - self._last_action > ACTION_COOLDOWN:
                    self._last_action = seconds()
                    button.press(self)
            connection.on_shoot_set(self, fire)

        def on_animation_update(self, jump, crouch, sneak, sprint):
            if self.tool == SPADE_TOOL and sneak:
                state = self.state_stack.top()
                button, platform = self._get_button_or_platform_if_within_reach()
                if button and isinstance(state, NeedsButtonState):
                    self.send_chat(str(button))
                elif platform and isinstance(state, NeedsPlatformState):
                    self.send_chat(str(platform))
            return connection.on_animation_update(self, jump, crouch, sneak, sprint)

        def on_command(self, command, parameters):
            if command == 'where' and not parameters:
                self.where_location = self.world_object.position.get()
                self.where_orientation = self.world_object.orientation.get()
            connection.on_command(self, command, parameters)

        def _get_button_or_platform_if_within_reach(self):
            location = self.world_object.cast_ray(ACTION_RAY_LENGTH)
            if location is None:
                return None, None
            return self.protocol.get_button(location), self.protocol.get_platform(location)

        #
        # def on_reset(self):
        #     self.where_location = None
        #     self.where_orientation = None
        #     self.last_action = None
        #     self.previous_button = None
        #     self.previous_platform = None
        #     connection.on_reset(self)
        #
        # def on_disconnect(self):
        #     for trigger in self.protocol.position_triggers:
        #         trigger.callback(self)
        #     connection.on_disconnect(self)

    return PlatformConnection
