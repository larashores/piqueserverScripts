from piqueserver.commands import command
from cbc.twoblockcommand import two_block_command, two_block_protocol, two_block_connection
from cbc import cbc, clearbox


@command('db')
def db(connection):
    return two_block_command(connection,
                             'Break first corner block',
                             'DeBox cancelled')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)

    class ClearBoxMakerConnection(two_block_connection(connection)):
        second_message = 'Now break opposite corner block'
        finished_message = 'Destroying box!'

        def chosen_func(self, point1, point2):
            clearbox.clear(self.protocol,
                           point1.x, point1.y, point1.z, point2.x, point2.y, point1.z,
                           self.god)

        def on_block_removed(self, x, y, z):
            return self.handle_block(x, y, z)

    return two_block_protocol(protocol), ClearBoxMakerConnection
