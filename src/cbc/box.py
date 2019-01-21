from piqueserver.commands import command
from cbc import cbc, buildbox
from cbc.choosestatus import ChooseStatus


@command('box')
def box(connection, filled=""):
    if connection.boxing != ChooseStatus.NOT_CHOOSING:
        connection.boxing = ChooseStatus.NOT_CHOOSING
        return 'Building generator cancelled'
    else:
        connection.boxing = ChooseStatus.CHOOSING_FIRST_BLOCK
        connection.boxing_filled = filled.lower() == "filled"
        return 'Place first corner block'


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    
    class BoxMakerConnection(connection):
        def __init__(self, *arg, **kw):
            connection.__init__(self, *arg, **kw)
            self.boxing = ChooseStatus.NOT_CHOOSING
            self.boxing_filled = False
            self.box_x = 0
            self.box_y = 0
            self.box_z = 0
        
        def build_box_filled(self, x1, y1, z1, x2, y2, z2, color=None):
            buildbox.build_filled(self.protocol, x1, y1, z1, x2, y2, z2, color or self.color, self.god, self.god_build)
        
        def build_box(self, x1, y1, z1, x2, y2, z2, color = None):
            buildbox.build_empty(self.protocol, x1, y1, z1, x2, y2, z2, color or self.color, self.god, self.god_build)
        
        def on_block_build(self, x, y, z):
            if self.boxing == ChooseStatus.CHOOSING_SECOND_BLOCK:
                self.boxing = ChooseStatus.NOT_CHOOSING
                if not self.boxing_filled:
                    self.build_box(self.box_x, self.box_y, self.box_z, x, y, z)
                else:
                    self.build_box_filled(self.box_x, self.box_y, self.box_z, x, y, z)
                self.send_chat('Box created!')
            if self.boxing == ChooseStatus.CHOOSING_FIRST_BLOCK:
                self.box_x = x
                self.box_y = y
                self.box_z = z
                self.send_chat('Now place opposite corner block')
                self.boxing = ChooseStatus.CHOOSING_SECOND_BLOCK
            return connection.on_block_build(self, x, y, z)
    
    class BoxMakerProtocol(protocol):
        def on_map_change(self, map_):
            for connection in self.connections.values():
                connection.boxing = ChooseStatus.NOT_CHOOSING
            protocol.on_map_change(self, map_)
    
    return BoxMakerProtocol, BoxMakerConnection
