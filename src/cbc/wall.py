from piqueserver.commands import command
from cbc.wallcommand import wall_command, wall_connection
from cbc import cbc, buildbox, util


@command('wall')
def wall(connection, value=''):
    return wall_command(connection, value,
                        'Building {} block high wall. "/wall" to cancel.',
                        'No longer building wall. Activate with `/wall 64` to `/wall -64`')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)

    class WallMakerConnection(wall_connection(connection)):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.walling = None

        def wall_func(self, x1, y1, z1, x2, y2, z2):
            buildbox.build_filled(self.protocol, x1, y1, z1, x2, y2, z2,
                                  self.color, self.god, self.god_build)

        def on_block_build(self, x, y, z):
            self.handle_block(x, y, z)
            return connection.on_block_build(self, x, y, z)

    return protocol, WallMakerConnection
