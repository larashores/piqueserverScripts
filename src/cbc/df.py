from piqueserver.commands import command
from cbc.twoblockcommand import two_block_command, two_block_protocol, two_block_connection
from cbc import clearbox, cbc


@command('df')
def df(connection):
    return two_block_command(connection,
                             'Place first corner block',
                             'DeFloor cancelled')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)

    class ClearFloorMakerConnection(two_block_connection(connection)):
        second_message = 'Now break opposite corner block'
        finished_message = 'Floor destroyed!'

        def chosen_func(self, point1, point2):
            if point1.z != point2.z:
                self.send_chat('Surface is uneven! Using first height.')
                clearbox.clear_solid(self.protocol,
                                     point1.x, point1.y, point1.z,
                                     point2.x, point2.y, point1.z, self.god)

        def on_block_removed(self, x, y, z):
            return self.handle_block(x, y, z)

    return two_block_protocol(protocol), ClearFloorMakerConnection
