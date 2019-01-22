from piqueserver.commands import command
from cbc.twoblockcommand import two_block_command, two_block_protocol, two_block_connection
from cbc import buildbox, cbc


@command('floor')
def floor(connection):
    return two_block_command(connection,
                             'Place first corner block',
                             'Floor generator cancelled')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)

    class FloorMakerConnection(two_block_connection(connection)):
        second_message = 'Now place opposite corner block'
        finished_message = 'Floor created!'

        def on_apply(self, point1, point2):
            if point1.z != point2.z:
                self.send_chat('Surface is uneven! Using first height.')
                buildbox.build_filled(self.protocol,
                                      point1.x, point1.y, point1.z,
                                      point2.x, point2.y, point1.z,
                                      self.color, self.god, self.god_build)

    return two_block_protocol(protocol), FloorMakerConnection
