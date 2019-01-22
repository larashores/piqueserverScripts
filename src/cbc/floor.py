from piqueserver.commands import command
from cbc.core.selecttwostate import SelectTwoState, select_two_command
from cbc.core import buildbox, cbc, buildingstate


@command('floor')
def floor(connection):
    return select_two_command(connection, FloorState)


class FloorState(SelectTwoState):
    START_MESSAGE = 'You are now in *Floor* mode. Place first corner block.'
    FINISH_MESSAGE = 'Creating floor!'
    CANCEL_MESSAGE = 'Floor creation canceled.'
    CHOOSE_SECOND_MESSAGE = 'Now place opposite corner block'
    BUILD_STATE = True

    def on_apply(self, point1, point2):
        player = self.player
        if point1.z != point2.z:
            player.send_chat('Surface is uneven! Using first height.')
        buildbox.build_filled(player.protocol,
                              point1.x, point1.y, point1.z,
                              point2.x, point2.y, point1.z,
                              player.color, player.god, player.god_build)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    protocol, connection = buildingstate.apply_script(protocol, connection, config)

    return protocol, connection
