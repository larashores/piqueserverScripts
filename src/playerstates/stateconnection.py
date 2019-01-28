from playerstates.statestack import StateStack
from playerstates.buildingstate import BuildingState


def state_connection(connection):
    if hasattr(connection, '__state_connection__'):
        return connection

    class StateConnection(connection):
        __state_connection__ = True

        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.state_stack = StateStack(self)

        def on_block_removed(self, x, y, z):
            state = self.state_stack.top()
            if isinstance(state, BuildingState):
                state.on_block_removed(x, y, z)
            connection.on_block_removed(self, x, y, z)

        def on_block_build(self, x, y, z):
            state = self.state_stack.top()
            if isinstance(state, BuildingState):
                state.on_block_build(x, y, z)
            connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            state = self.state_stack.top()
            if isinstance(state, BuildingState):
                state.on_line_build(points)
            connection.on_line_build(self, points)

        def on_line_build_attempt(self, points):
            if connection.on_line_build_attempt(self, points) is False:
                return False
            state = self.state_stack.top()
            if isinstance(state, BuildingState):
                return state.on_line_build_attempt(points)
            return True

    return StateConnection
