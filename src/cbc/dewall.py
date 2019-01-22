from piqueserver.commands import command
from cbc.core.wallstate import WallState, wall_command
from cbc.core import cbc, clearbox, buildingstate


@command('dw')
def dewall(connection, value=''):
    return wall_command(connection, value, DeWallState)


class DeWallState(WallState):
    START_MESSAGE = 'You are now in *De-Wall* mode. "/dw" to cancel.'
    CANCEL_MESSAGE = 'You are no longer in *De-Wall* mode.'
    BUILD_STATE = False

    def on_apply(self, x1, y1, z1, x2, y2, z2):
        player = self.player
        clearbox.clear_solid(player.protocol, x1, y1, z1, x2, y2, z2, player.god)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    protocol, connection = buildingstate.apply_script(protocol, connection, config)

    return protocol, connection
