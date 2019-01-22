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

    class WallMakerConnection(wall_connection(connection, True)):
        def on_apply(self, x1, y1, z1, x2, y2, z2):
            buildbox.build_filled(self.protocol, x1, y1, z1, x2, y2, z2,
                                  self.color, self.god, self.god_build)

    return protocol, WallMakerConnection
