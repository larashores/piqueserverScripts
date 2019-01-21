from piqueserver.commands import command
from cbc.choosestatus import ChooseStatus
from cbc import cbc, clearbox


@command('db')
def db(connection):
    if connection.deboxing != ChooseStatus.NOT_CHOOSING:
        connection.deboxing = ChooseStatus.NOT_CHOOSING
        return 'DeBox cancelled'
    else:
        connection.deboxing = ChooseStatus.CHOOSING_FIRST_BLOCK
        return 'Break first corner block'


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    
    class ClearBoxMakerConnection(connection):
        def __init__(self, *arg, **kw):
            connection.__init__(self, *arg, **kw)
            self.deboxing = 0
            self.clearbox_x = 0
            self.clearbox_y = 0
            self.clearbox_z = 0
        
        def clear_box_solid(self, x1, y1, z1, x2, y2, z2):
            clearbox.clear_solid(self.protocol, x1, y1, z1, x2, y2, z2, self.god)
        
        def clear_box(self, x1, y1, z1, x2, y2, z2):
            clearbox.clear(self.protocol, x1, y1, z1, x2, y2, z2, self.god)
        
        def on_block_removed(self, x, y, z):
            if self.deboxing == ChooseStatus.CHOOSING_SECOND_BLOCK:
                self.deboxing = ChooseStatus.NOT_CHOOSING
                self.clear_box(self.clearbox_x, self.clearbox_y, self.clearbox_z, x, y, z)
                self.send_chat('Destroying box!')
            if self.deboxing == ChooseStatus.CHOOSING_FIRST_BLOCK:
                self.clearbox_x = x
                self.clearbox_y = y
                self.clearbox_z = z
                self.send_chat('Now break opposite corner block')
                self.deboxing = ChooseStatus.CHOOSING_SECOND_BLOCK
            return connection.on_block_removed(self, x, y, z)
    
    class ClearBoxMakerProtocol(protocol):
        def on_map_change(self, map_):
            for connection in self.connections.values():
                connection.deboxing = ChooseStatus.NOT_CHOOSING
            protocol.on_map_change(self, map_)
    
    return ClearBoxMakerProtocol, ClearBoxMakerConnection
