from piqueserver.commands import command
from cbc.buildorclearcommand import build_or_clear_connection
from cbc import cbc, buildbox, clearbox, util
from abc import abstractmethod, ABCMeta

STRING_NO_WALL = 'No longer {} wall. Activate with `/wall 64` to `/wall -64`'


@command('wall')
def wall_command(connection, height, string_on, string_off):
    if height == '':
        connection.walling = None
        return string_off
    try:
        height = int(height)
    except ValueError:
        return 'Invalid height'
    if not (-65 < height < 65):
        return 'Height out of range (Must be between -64 and 65'
    if abs(height) > 1:
        connection.walling = height
        return string_on.format(height)
    else:
        return string_off


def wall_connection(connection, build):
    class WallConnection(build_or_clear_connection(connection, build), metaclass=ABCMeta):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self._walling = None

        @abstractmethod
        def on_apply(self, x1, y1, z1, x2, y2, z2):
            pass

        def on_block(self, x, y, z):
            if self._walling is not None:
                z2 = min(61, max(0, z - self._walling + util.sign(self._walling)))
                self.on_apply(x, y, z, x, y, z2)

    return WallConnection
