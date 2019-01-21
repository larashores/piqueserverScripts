from piqueserver.commands import command
from cbc.choosestatus import ChooseStatus
from cbc import clearbox, cbc


@command('df')
def df(connection):
    if connection.deflooring != ChooseStatus.NOT_CHOOSING:
        connection.deflooring = ChooseStatus.NOT_CHOOSING
        return 'DeFloor cancelled'
    else:
        connection.deflooring = ChooseStatus.CHOOSING_FIRST_BLOCK
        return 'Break first corner block'


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    
    class ClearFloorMakerConnection(connection):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.deflooring = ChooseStatus.NOT_CHOOSING
            self.clearfloor_x = 0
            self.clearfloor_y = 0
            self.clearfloor_z = 0
        
        def on_block_removed(self, x, y, z):
            if self.deflooring == ChooseStatus.CHOOSING_SECOND_BLOCK:
                self.deflooring = ChooseStatus.NOT_CHOOSING
                if self.clearfloor_z != z:
                    self.send_chat('Surface is uneven! Using first height.')
                clearbox.clear_solid(self.protocol, self.clearfloor_x, self.clearfloor_y, self.clearfloor_z,
                                     x, y, self.clearfloor_z, self.god)
                self.send_chat('Floor destroyed!')
            if self.deflooring == ChooseStatus.CHOOSING_FIRST_BLOCK:
                self.clearfloor_x = x
                self.clearfloor_y = y
                self.clearfloor_z = z
                self.send_chat('Now break opposite corner block')
                self.deflooring = ChooseStatus.CHOOSING_SECOND_BLOCK
            return connection.on_block_removed(self, x, y, z)
    
    class ClearFloorMakerProtocol(protocol):
        def on_map_change(self, map_):
            for connection in self.connections.values():
                connection.deflooring = ChooseStatus.NOT_CHOOSING
            protocol.on_map_change(self, map_)
    
    return ClearFloorMakerProtocol, ClearFloorMakerConnection
