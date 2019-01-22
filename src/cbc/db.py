from piqueserver.commands import command
from cbc.core.twoblockcommand import two_block_command, two_block_protocol, two_block_connection
from cbc.core import cbc, clearbox


@command('db')
def db(connection):
    return two_block_command(connection,
                             'Break first corner block',
                             'DeBox cancelled')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)

    class ClearBoxMakerConnection(two_block_connection(connection, False)):
        second_message = 'Now break opposite corner block'
        finished_message = 'Destroying box!'

        def on_apply(self, point1, point2):
            clearbox.clear(self.protocol, point1.x, point1.y, point1.z, point2.x, point2.y, point1.z, self.god)

    return two_block_protocol(protocol), ClearBoxMakerConnection
