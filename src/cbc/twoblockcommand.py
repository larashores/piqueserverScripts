from enum import IntEnum


class ChooseStatus(IntEnum):
    NOT_CHOOSING = 0
    CHOOSING_FIRST_BLOCK = 1
    CHOOSING_SECOND_BLOCK = 2


def two_block_command(connection, start_message, cancel_message):
    if connection.choosing != ChooseStatus.NOT_CHOOSING:
        connection.choosing = ChooseStatus.NOT_CHOOSING
        return cancel_message
    else:
        connection.choosing = ChooseStatus.CHOOSING_FIRST_BLOCK
        return start_message


def two_block_protocol(protocol):
    class TwoBlockProtocol(protocol):
        def on_map_change(self, map_):
            for connection in self.connections.values():
                connection.choosing = ChooseStatus.NOT_CHOOSING
            protocol.on_map_change(self, map_)
    return TwoBlockProtocol
