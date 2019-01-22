from piqueserver.commands import command
from cbc.core.wallcommand import wall_command, wall_connection
from cbc.core import cbc, clearbox


@command('dw')
def dw(connection, value=''):
    return wall_command(connection, value,
                        'DeWalling {} block high wall. "/dw" to cancel.',
                        'No longer DeWalling. Activate with `/dw 64` to `/dw -64`')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)

    class DeWallMakerConnection(wall_connection(connection, False)):
        def on_apply(self, x1, y1, z1, x2, y2, z2):
            clearbox.clear_solid(self.protocol, x1, y1, z1, x2, y2, z2, self.god)

    return protocol, DeWallMakerConnection
