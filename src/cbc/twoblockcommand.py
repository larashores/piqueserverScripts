from enum import IntEnum
from abc import abstractmethod, ABCMeta
from cbc.buildorclearcommand import build_or_clear_connection


class _Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


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


def two_block_connection(connection, build):
    class TwoBlockConnection(build_or_clear_connection(connection, build), metaclass=ABCMeta):
        second_message = ''
        finished_message = ''

        def __init__(self, *arg, **kwargs):
            connection.__init__(self, *arg, **kwargs)
            self._choosing = ChooseStatus.NOT_CHOOSING
            self._first_point = _Point(0, 0, 0)

        @abstractmethod
        def on_apply(self, point1, point2):
            pass

        def on_block(self, x, y, z):
            point = _Point(x, y, z)
            if self._choosing == ChooseStatus.CHOOSING_SECOND_BLOCK:
                self._choosing = ChooseStatus.NOT_CHOOSING
                self.on_apply(self._first_point, point)
                self.send_chat(self.finished_message)
            if self._choosing == ChooseStatus.CHOOSING_FIRST_BLOCK:
                self._first_point = point
                self.send_chat(self.second_message)
                self._choosing = ChooseStatus.CHOOSING_SECOND_BLOCK

    return TwoBlockConnection
