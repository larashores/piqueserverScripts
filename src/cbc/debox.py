from piqueserver.commands import command
from cbc.core.selecttwostate import SelectTwoState, select_two_command
from cbc.core import cbc, clearbox, buildingstate


@command('db')
def debox(connection):
    return select_two_command(connection, DeBoxState)


class DeBoxState(SelectTwoState):
    START_MESSAGE = 'You are now *De-Box* mode. Break first corner block'
    FINISH_MESSAGE = 'Destroying box!'
    CANCEL_MESSAGE = 'Box destruction canceled.'
    CHOOSE_SECOND_MESSAGE = 'Now break opposite corner block.'
    BUILD_STATE = False

    def on_apply(self, point1, point2):
        player = self.player
        clearbox.clear(player.protocol, point1.x, point1.y, point1.z, point2.x, point2.y, point1.z, player.god)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    protocol, connection = buildingstate.apply_script(protocol, connection, config)

    return protocol, connection
