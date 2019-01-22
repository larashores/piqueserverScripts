from piqueserver.commands import command
from cbc.core.selecttwostate import SelectTwoState, select_two_command
from cbc.core import clearbox, cbc, buildingstate


@command('df')
def defloor(connection):
    return select_two_command(connection, DeFloorState)


class DeFloorState(SelectTwoState):
    START_MESSAGE = 'You are now deflooring. Place first corner block'
    FINISH_MESSAGE = 'Floor destroyed'
    CANCEL_MESSAGE = 'Deflooring canceled'
    CHOOSE_SECOND_MESSAGE = 'Now break opposite corner block'
    BUILD_STATE = True

    def on_apply(self, point1, point2):
        player = self.player
        if point1.z != point2.z:
            player.send_chat('Surface is uneven! Using first height.')
        clearbox.clear_solid(player.protocol,
                             point1.x, point1.y, point1.z,
                             point2.x, point2.y, point1.z, player.god)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    protocol, connection = buildingstate.apply_script(protocol, connection, config)

    return protocol, connection
