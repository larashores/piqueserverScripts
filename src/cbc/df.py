from piqueserver.commands import command
from cbc.twoblockcommand import two_block_command, two_block_protocol, ChooseStatus
from cbc import clearbox, cbc


@command('df')
def df(connection):
    return two_block_command(connection,
                             'Place first corner block',
                             'DeFloor cancelled')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    
    class ClearFloorMakerConnection(connection):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.choosing = ChooseStatus.NOT_CHOOSING
            self.clearfloor_x = 0
            self.clearfloor_y = 0
            self.clearfloor_z = 0
        
        def on_block_removed(self, x, y, z):
            if self.choosing == ChooseStatus.CHOOSING_SECOND_BLOCK:
                self.choosing = ChooseStatus.NOT_CHOOSING
                if self.clearfloor_z != z:
                    self.send_chat('Surface is uneven! Using first height.')
                clearbox.clear_solid(self.protocol, self.clearfloor_x, self.clearfloor_y, self.clearfloor_z,
                                     x, y, self.clearfloor_z, self.god)
                self.send_chat('Floor destroyed!')
            if self.choosing == ChooseStatus.CHOOSING_FIRST_BLOCK:
                self.clearfloor_x = x
                self.clearfloor_y = y
                self.clearfloor_z = z
                self.send_chat('Now break opposite corner block')
                self.choosing = ChooseStatus.CHOOSING_SECOND_BLOCK
            return connection.on_block_removed(self, x, y, z)

    return two_block_protocol(protocol), ClearFloorMakerConnection
