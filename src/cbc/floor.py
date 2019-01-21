from piqueserver.commands import command
from cbc.choosestatus import ChooseStatus
from cbc import buildbox, cbc


@command('floor')
def floor(connection):
    if connection.flooring != ChooseStatus.NOT_CHOOSING:
        connection.flooring = ChooseStatus.NOT_CHOOSING
        return 'Floor generator cancelled'
    else:
        connection.flooring = ChooseStatus.CHOOSING_FIRST_BLOCK
        return 'Place first corner block'


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    
    class FloorMakerConnection(connection):
        def __init__(self, *arg, **kwargs):
            connection.__init__(self, *arg, **kwargs)
            self.flooring = ChooseStatus.NOT_CHOOSING
            self.floor_x = 0
            self.floor_y = 0
            self.floor_z = 0
        
        def on_block_build(self, x, y, z):
            if self.flooring == ChooseStatus.CHOOSING_SECOND_BLOCK:
                self.flooring = ChooseStatus.NOT_CHOOSING
                if self.floor_z != z:
                    self.send_chat('Surface is uneven! Using first height.')
                buildbox.build_filled(self.protocol, self.floor_x, self.floor_y, self.floor_z,
                                      x, y, self.floor_z, self.color, self.god, self.god_build)
            if self.flooring == ChooseStatus.CHOOSING_FIRST_BLOCK:
                self.floor_x = x
                self.floor_y = y
                self.floor_z = z
                self.send_chat('Now place opposite corner block')
                self.flooring = ChooseStatus.CHOOSING_SECOND_BLOCK
            return connection.on_block_build(self, x, y, z)
    
    class FloorMakerProtocol(protocol):
        def on_map_change(self, map_):
            for connection in self.connections.values():
                connection.flooring = ChooseStatus.NOT_CHOOSING
            protocol.on_map_change(self, map_)
    
    return FloorMakerProtocol, FloorMakerConnection
