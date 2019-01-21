from piqueserver.commands import command
from cbc.twoblockcommand import two_block_command, two_block_protocol, ChooseStatus
from cbc import cbc, clearbox


@command('db')
def db(connection):
    return two_block_command(connection,
                             'Break first corner block',
                             'DeBox cancelled')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    
    class ClearBoxMakerConnection(connection):
        def __init__(self, *arg, **kw):
            connection.__init__(self, *arg, **kw)
            self.choosing = 0
            self.clearbox_x = 0
            self.clearbox_y = 0
            self.clearbox_z = 0
        
        def clear_box_solid(self, x1, y1, z1, x2, y2, z2):
            clearbox.clear_solid(self.protocol, x1, y1, z1, x2, y2, z2, self.god)
        
        def clear_box(self, x1, y1, z1, x2, y2, z2):
            clearbox.clear(self.protocol, x1, y1, z1, x2, y2, z2, self.god)
        
        def on_block_removed(self, x, y, z):
            if self.choosing == ChooseStatus.CHOOSING_SECOND_BLOCK:
                self.choosing = ChooseStatus.NOT_CHOOSING
                self.clear_box(self.clearbox_x, self.clearbox_y, self.clearbox_z, x, y, z)
                self.send_chat('Destroying box!')
            if self.choosing == ChooseStatus.CHOOSING_FIRST_BLOCK:
                self.clearbox_x = x
                self.clearbox_y = y
                self.clearbox_z = z
                self.send_chat('Now break opposite corner block')
                self.choosing = ChooseStatus.CHOOSING_SECOND_BLOCK
            return connection.on_block_removed(self, x, y, z)

    return two_block_protocol(protocol), ClearBoxMakerConnection
