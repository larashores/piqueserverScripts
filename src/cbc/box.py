from piqueserver.commands import command
from cbc.core.selecttwostate import SelectTwoState, select_two_command
from cbc.core import buildbox, cbc, buildingstate


@command('box')
def box(connection, filled=""):
    return select_two_command(connection, BoxState, filled.lower() == "filled")


class BoxState(SelectTwoState):
    START_MESSAGE = 'You are now in *Box* mode. Place first corner block.'
    FINISH_MESSAGE = 'Creating box!'
    CANCEL_MESSAGE = 'Box creation canceled.'
    CHOOSE_SECOND_MESSAGE = 'Now place opposite corner block.'
    BUILD_STATE = True

    def __init__(self, player, filled):
        SelectTwoState.__init__(self, player)
        self._filled = filled

    def on_apply(self, point1, point2):
        player = self.player
        build_function = buildbox.build_filled if self._filled else buildbox.build_empty
        build_function(self.player.protocol,
                       point1.x, point1.y, point1.z, point2.x, point2.y, point2.z,
                       player.color, player.god, player.god_build)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    protocol, connection = buildingstate.apply_script(protocol, connection, config)

    return protocol, connection
