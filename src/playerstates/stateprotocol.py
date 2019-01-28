def state_protocol(protocol):
    if hasattr(protocol, '__state_protocol__'):
        return protocol

    class BuildingStateProtocol(protocol):
        __state_protocol__ = True

        def on_map_change(self, map_):
            for connection in self.connections.values():
                connection.state_stack.clear()
            protocol.on_map_change(self, map_)

    return BuildingStateProtocol
