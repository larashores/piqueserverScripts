from playerstates.statestack import StateStack


def apply_script(protocol, connection, config):

    if hasattr(protocol, '__building_state_script_applied__'):
        return protocol, connection

    class BuildingStateProtocol(protocol):
        __building_state_script_applied__ = True

        def on_map_change(self, map_):
            for connection in self.connections.values():
                connection.state_stack.clear()
            protocol.on_map_change(self, map_)

    class BuildingStateConnection(connection):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.state_stack = StateStack()

        def on_block_removed(self, x, y, z):
            state = self.state_stack.top()
            if state:
                state.on_block_removed(x, y, z)
            connection.on_block_removed(self, x, y, z)

        def on_block_build(self, x, y, z):
            state = self.state_stack.top()
            if state:
                state.on_block_build(x, y, z)
            connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            state = self.state_stack.top()
            if state:
                state.on_line_build(points)
            connection.on_line_build(self, points)

        def on_line_build_attempt(self, points):
            state = self.state_stack.top()
            if connection.on_line_build_attempt(self, points) is False:
                return False
            if state:
                return state.on_line_build_attempt(points)
            return True

    return BuildingStateProtocol, BuildingStateConnection
