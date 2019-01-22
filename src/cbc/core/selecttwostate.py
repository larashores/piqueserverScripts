from enum import IntEnum
from abc import abstractmethod, ABCMeta
from cbc.core.buildorremovestate import BuildOrRemoveState


def select_two_command(connection, select_two_state_type):
    if type(connection.state) == select_two_state_type:
        connection.state = None
        return
    connection.state = select_two_state_type(connection)


class SelectTwoState(BuildOrRemoveState, metaclass=ABCMeta):
    CHOOSE_SECOND_MESSAGE = ''

    def __init__(self, *args, **kwargs):
        BuildOrRemoveState.__init__(self, *args, **kwargs)
        self._choosing = _ChooseStatus.CHOOSING_FIRST_BLOCK
        self._first_point = _Point(0, 0, 0)

    @abstractmethod
    def on_apply(self, point1, point2):
        pass

    def on_block(self, x, y, z):
        point = _Point(x, y, z)
        if self._choosing == _ChooseStatus.CHOOSING_SECOND_BLOCK:
            self.on_apply(self._first_point, point)
            self.player.state_finished()
        if self._choosing == _ChooseStatus.CHOOSING_FIRST_BLOCK:
            self._first_point = point
            self.player.send_chat(self.CHOOSE_SECOND_MESSAGE)
            self._choosing = _ChooseStatus.CHOOSING_SECOND_BLOCK


class _ChooseStatus(IntEnum):
    CHOOSING_FIRST_BLOCK = 0
    CHOOSING_SECOND_BLOCK = 1


class _Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
