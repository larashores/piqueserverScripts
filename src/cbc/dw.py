from piqueserver.commands import command
from cbc.wallcommand import wall_command, wall_connection
from cbc import cbc, clearbox


@command('dw')
def dw(connection, value=''):
    return wall_command(connection, value,
                        'DeWalling {} block high wall. "/dw" to cancel.',
                        'No longer DeWalling. Activate with `/dw 64` to `/dw -64`')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)

    class DeWallMakerConnection(wall_connection(connection)):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.walling = None

        def wall_func(self, x1, y1, z1, x2, y2, z2):
            clearbox.clear_solid(self.protocol, x1, y1, z1, x2, y2, z2, self.god)

        def on_block_removed(self, x, y, z):
            self.handle_block(x, y, z)
            return connection.on_block_removed(self, x, y, z)

    return protocol, DeWallMakerConnection
