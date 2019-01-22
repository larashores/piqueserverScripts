from piqueserver.commands import command
from cbc.core.buildorremovestate import BuildOrRemoveState
from cbc.core import util
from abc import abstractmethod, ABCMeta


@command('wall')
def wall_command(connection, height, wall_state_type):
    if type(connection.state) == wall_state_type and height == '':
        connection.state = None
    try:
        height = int(height)
    except ValueError:
        return 'Invalid height'
    if not (-65 < height < 65) or height == 0:
        return 'Height out of range (Must be between -64 and 65 but not 0)'
    if abs(height) > 1:
        connection.state = wall_state_type(connection, height)


class WallState(BuildOrRemoveState, metaclass=ABCMeta):

    def __init__(self, player, wall_height):
        BuildOrRemoveState.__init__(self, player)
        self._wall_height = wall_height

    @abstractmethod
    def on_apply(self, x1, y1, z1, x2, y2, z2):
        pass

    def on_block(self, x, y, z):
        z2 = min(61, max(0, z - self._wall_height + util.sign(self._wall_height)))
        self.on_apply(x, y, z, x, y, z2)
