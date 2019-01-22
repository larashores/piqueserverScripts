class BuildingState:
    START_MESSAGE = ''
    FINISH_MESSAGE = ''
    CANCEL_MESSAGE = ''

    def __init__(self, player=None):
        self.player = player

    def on_block_removed(self, x, y, z):
        pass

    def on_block_build(self, x, y, z):
        pass

    def on_line_build(self, points):
        pass


def apply_script(protocol, connection, config):
    class StateProtocol(protocol):
        def on_map_change(self, map_):
            for connection in self.connections.values():
                connection.state = None
            protocol.on_map_change(self, map_)

    class StateConnection(connection):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self._current_state = None

        @property
        def state(self):
            return self._current_state

        @state.setter
        def state(self, new_state):
            old_state = self._current_state
            if old_state and old_state.CANCEL_MESSAGE:
                self.send_chat(old_state.CANCEL_MESSAGE)
            if new_state and new_state.START_MESSAGE:
                self.send_chat(new_state.START_MESSAGE)
            self._current_state = new_state

        def state_finished(self):
            old_state = self._current_state
            if old_state and old_state.FINISH_MESSAGE:
                self.send_chat(self._current_state.FINISH_MESSAGE)
            self._current_state = None

        def on_block_removed(self, x, y, z):
            if self._current_state:
                self._current_state.on_block_removed(x, y, z)
            connection.on_block_removed(self, x, y, z)

        def on_block_build(self, x, y, z):
            if self._current_state:
                self._current_state.on_block_build(x, y, z)
            connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            if self._current_state:
                self._current_state.on_line_build(points)
            connection.on_line_build(self, points)

    return StateProtocol, StateConnection
