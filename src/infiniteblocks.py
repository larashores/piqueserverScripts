"""
Automatically refills a players blocks, similarly to how it is done in god mode, but without other effects
"""

from piqueserver.commands import command


@command('infiniteblocks', 'ib')
def infinite_blocks(connection):
    protocol = connection.protocol
    if connection not in protocol.players:
        raise ValueError()
    connection.god = False
    connection.infinite_blocks = not connection.infinite_blocks
    if connection.infinite_blocks:
        message = '{} entered INFINITE BLOCKS MODE'.format(connection.name)
    else:
        message = '%s returned to being a mere sightseer'.format(connection.name)
    connection.protocol.send_chat(message, irc=True)


def apply_script(protocol, connection, config):
    class InfiniteBlocksConnection(connection):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.infinite_blocks = False

        def on_hit(self, hit_amount, player, type_, grenade):
            def check_infinite(check_player, msg):
                if check_player.infinite_blocks:
                    if not player.invisible:
                        self.send_chat(msg)
                    return False
                return True
            if not check_infinite(self, "You can't hurt people while you are in *Infinite Blocks Mode*"):
                return False
            if not check_infinite(player, "You can't hurt %s! That player is in *Infinite Blocks Mode*" % player.name):
                return False
            return connection.on_hit(self, hit_amount, player, type_, grenade)

        def on_block_build(self, x, y, z):
            if self.infinite_blocks:
                self.refill()
            return connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            if self.infinite_blocks:
                self.refill()
            return connection.on_line_build(self, points)

    return protocol, InfiniteBlocksConnection
