from piqueserver.commands import command
from cbc.core.wallstate import WallState, wall_command
from cbc.core import cbc, clearbox, buildingstate


@command('dw')
def dw(connection, value=''):
    return wall_command(connection, value, DeWallState)


class DeWallState(WallState):
    START_MESSAGE = 'Destroying walls. "/wall" to cancel.'
    CANCEL_MESSAGE = 'No longer destroying walls. Activate with `/dw 64` to `/dw -64`'
    BUILD_STATE = False

    def on_apply(self, x1, y1, z1, x2, y2, z2):
        player = self.player
        clearbox.clear_solid(player.protocol, x1, y1, z1, x2, y2, z2, player.god)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    protocol, connection = buildingstate.apply_script(protocol, connection, config)

    return protocol, connection
