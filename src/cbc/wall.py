from piqueserver.commands import command
from cbc.core.wallstate import WallState, wall_command
from cbc.core import cbc, buildbox, buildingstate


@command('wall')
def wall(connection, height=''):
    return wall_command(connection, height, BuildWallState)


class BuildWallState(WallState):
    START_MESSAGE = 'You are now in *Wall* mode. "/wall" to cancel.'
    CANCEL_MESSAGE = 'You are no longer in *Wall* mode.'
    BUILD_STATE = True

    def on_apply(self, x1, y1, z1, x2, y2, z2):
        player = self.player
        buildbox.build_filled(player.protocol, x1, y1, z1, x2, y2, z2,
                              player.color, player.god, player.god_build)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    protocol, connection = buildingstate.apply_script(protocol, connection, config)

    return protocol, connection
