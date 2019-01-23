
def player_action(player, select, inspect):
    if not select and not inspect:
        return
    protocol = player.protocol
    if not protocol.platforms and not protocol.buttons:
        return
    state = player.states.top()
    if inspect and not state and not select:
        return
    last_action = player.last_action
    if last_action is not None and seconds() - last_action <= ACTION_COOLDOWN:
        return
    player.last_action = seconds()
    location = player.world_object.cast_ray(player.reach)
    if location is None:
        return
    x, y, z = location

    button = protocol.buttons.get(location)
    if button:
        if state:
            if select and state.name == 'select button':
                state.button = button
                player.states.pop()
                return
            elif inspect and 'button' in state.name:
                info = S_BUTTON_INFO.format(label = button.label,
                    cooldown = button.cooldown)
                player.send_chat(info)
                return
        if not inspect:
            for trigger in button.triggers:
                if trigger.type == 'press':
                    trigger.callback(player)
    elif state and 'platform' in state.name:
        platform = protocol.get_platform(x, y, z)
        if select and state.name == 'select platform':
            if platform:
                state.platform = platform
                player.states.pop()
                return
            else:
                player.send_chat(S_NOT_A_PLATFORM)
        elif inspect:
            info = S_PLATFORM_INFO.format(label = platform.label,
                height = platform.height)
            player.send_chat(info)


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
                if state.name == 'new platform':
                    state.blocks.add((x, y, z))
                elif state.name == 'new button':
                    state.location = (x, y, z)
                    state.color = self.color
                    self.states.pop()
            connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            state = self.states.top()
            if state and state.name == 'new platform':
                state.blocks.update(points)
            connection.on_line_build(self, points)

        def on_block_destroy(self, x, y, z, mode):
            is_platform = self.protocol.is_platform
            if mode == DESTROY_BLOCK:
                if is_platform(x, y, z):
                    return False
            elif mode == SPADE_DESTROY:
                if (is_platform(x, y, z) or
                    is_platform(x, y, z + 1) or
                    is_platform(x, y, z - 1)):
                    return False
            elif mode == GRENADE_DESTROY:
                for i, j, k in prism(x - 1, y - 1, z - 1, x + 2, y + 2, z + 2):
                    if is_platform(i, j, k):
                        return False
            return connection.on_block_destroy(self, x, y, z, mode)

        def on_block_removed(self, x, y, z):
            state = self.states.top()
            if state and state.name == 'new platform':
                state.blocks.discard((x, y, z))
            connection.on_block_removed(self, x, y, z)

        def on_shoot_set(self, fire):
            if self.tool == SPADE_TOOL and fire:
                player_action(self, True, False)
            connection.on_shoot_set(self, fire)

        def on_position_update(self):
            if self.tool == SPADE_TOOL:
                player_action(self, self.world_object.primary_fire, False)
            connection.on_position_update(self)

        def on_orientation_update(self, x, y, z):
            if self.tool == SPADE_TOOL:
                player_action(self, self.world_object.primary_fire, False)
            return connection.on_orientation_update(self, x, y, z)

        def on_animation_update(self, jump, crouch, sneak, sprint):
            if self.tool == SPADE_TOOL:
                inspect = not self.world_object.sneak and sneak
                player_action(self, self.world_object.primary_fire, inspect)
            return connection.on_animation_update(self, jump, crouch, sneak,
                sprint)

        def on_command(self, command, parameters):
            if command == 'where' and not parameters:
                self.where_location = self.world_object.position.get()
                self.where_orientation = self.world_object.orientation.get()
            connection.on_command(self, command, parameters)
