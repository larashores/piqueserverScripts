from piqueserver.commands import command
from cbc.twoblockcommand import two_block_command, two_block_protocol, ChooseStatus
from cbc import cbc, buildbox


@command('box')
def box(connection, filled=""):
    connection.boxing_filled = filled.lower() == "filled"
    return two_block_command(connection,
                             'Place first corner block',
                             'Building generator cancelled')


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    
    class BoxMakerConnection(connection):
        def __init__(self, *arg, **kw):
            connection.__init__(self, *arg, **kw)
            self.choosing = ChooseStatus.NOT_CHOOSING
            self.boxing_filled = False
            self.box_x = 0
            self.box_y = 0
            self.box_z = 0
        
        def build_box_filled(self, x1, y1, z1, x2, y2, z2, color=None):
            buildbox.build_filled(self.protocol, x1, y1, z1, x2, y2, z2, color or self.color, self.god, self.god_build)
        
        def build_box(self, x1, y1, z1, x2, y2, z2, color = None):
            buildbox.build_empty(self.protocol, x1, y1, z1, x2, y2, z2, color or self.color, self.god, self.god_build)
        
        def on_block_build(self, x, y, z):
            if self.choosing == ChooseStatus.CHOOSING_SECOND_BLOCK:
                self.choosing = ChooseStatus.NOT_CHOOSING
                if not self.boxing_filled:
                    self.build_box(self.box_x, self.box_y, self.box_z, x, y, z)
                else:
                    self.build_box_filled(self.box_x, self.box_y, self.box_z, x, y, z)
                self.send_chat('Box created!')
            if self.choosing == ChooseStatus.CHOOSING_FIRST_BLOCK:
                self.box_x = x
                self.box_y = y
                self.box_z = z
                self.send_chat('Now place opposite corner block')
                self.choosing = ChooseStatus.CHOOSING_SECOND_BLOCK
            return connection.on_block_build(self, x, y, z)

    return two_block_protocol(protocol), BoxMakerConnection
