from twisted.internet.reactor import callLater, seconds
from pyspades.constants import SPADE_TOOL, GRENADE_DESTROY, DESTROY_BLOCK, SPADE_DESTROY
from platforms.states.platformsstate import PlatformsState
from platforms.worldobjects.trigger.presstrigger import PressTrigger
from platforms.util.geometry import prism_range

ACTION_RAY_LENGTH = 8.0
ACTION_RAY_LENGTH_LONG = 32.0
ACTION_COOLDOWN = 0.25


def platform_connection(connection):
    class PlatformConnection(connection):
        def __init__(self, *args, **kwargs):
            PlatformConnection.__init__(self, *args, **kwargs)
            self.where_location = None
            self.where_orientation = None
            self.last_action = None
            self.previous_button = None
            self.previous_platform = None
            self.reach = ACTION_RAY_LENGTH

        def on_reset(self):
            self.where_location = None
            self.where_orientation = None
            self.last_action = None
            self.previous_button = None
            self.previous_platform = None
            connection.on_reset(self)

        def on_disconnect(self):
            for trigger in self.protocol.position_triggers:
                trigger.callback(self)
            connection.on_disconnect(self)

        def on_block_destroy(self, x, y, z, mode):
            is_platform = self.protocol.is_platform
            if mode == DESTROY_BLOCK and is_platform(x, y, z):
                return False
            elif mode == SPADE_DESTROY:
                if is_platform(x, y, z) or is_platform(x, y, z + 1) or is_platform(x, y, z - 1):
                    return False
            elif mode == GRENADE_DESTROY:
                affected_blocks = prism_range(x - 1, y - 1, z - 1, x + 2, y + 2, z + 2)
                for i, j, k in affected_blocks:
                    if is_platform(i, j, k):
                        return False
            return connection.on_block_destroy(self, x, y, z, mode)

        def on_shoot_set(self, fire):
            if self.tool == SPADE_TOOL and fire:
                self.player_action(self, True, False)
            connection.on_shoot_set(self, fire)

        def on_position_update(self):
            if self.tool == SPADE_TOOL:
                self._player_action(self.world_object.primary_fire, False)
            return connection.on_position_update(self)

        def on_orientation_update(self, x, y, z):
            if self.tool == SPADE_TOOL:
                self._player_action(self.world_object.primary_fire, False)
            return connection.on_orientation_update(self, x, y, z)

        def on_animation_update(self, jump, crouch, sneak, sprint):
            if self.tool == SPADE_TOOL:
                self._player_action(self.world_object.primary_fire, not self.world_object.sneak and sneak)
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

        def _player_action(self, selecting, inspecting):
            if not selecting and not inspecting:
                return
            if not self.protocol.platforms and not self.protocol.buttons:
                return
            if self.last_action is not None and seconds() - self.last_action <= ACTION_COOLDOWN:
                return
            self.last_action = seconds()
            button = self._get_button_if_within_reach()
            platform = self._get_platform_if_within_reach()
            state = self.state_stack.top()
            if state and isinstance(state, PlatformsState):
                if selecting and state.on_select_button(button):
                    return
                elif inspecting and state.on_inspect_button(button):
                    return
                if selecting and state.on_select_platform(platform):
                    return
                elif inspecting and state.on_inspect_platform(platform):
                    return
            if button:
                for trigger in button.triggers:
                    if isinstance(trigger, PressTrigger):
                        trigger.callback(self)

    return PlatformConnection
