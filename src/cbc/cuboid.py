from pyspades.constants import *
from piqueserver.commands import command
from cbc.core import buildbox, clearbox, cbc, util, state

S_PLANE_USAGE = 'Usage: /plane <-x> <+x> <-y> <+y>'
S_PLANE_CANCEL = 'No longer plane-building'
S_PLANE = 'Dig or build to make or remove slabs, with the block as center. ' \
    'Abort with /plane'


@command('plane')
def plane(connection, *args):
    protocol = connection.protocol
    if connection not in protocol.players:
        raise ValueError()
    player = connection

    if isinstance(player.state, CuboidState) and not args:
        player.state = None
        return
    try:
        x1, x2, y1, y2 = util.parseargs('int int int int', args)
        player.state = CuboidState(x1, y1, x2, y2)
    except ValueError as err:
        player.send_chat(S_PLANE_USAGE)
        return str(err)


def plane_operation(player, x, y, z, size, value):
    theta = player.world_object.orientation
    th_cos, th_sin = int(round(theta.x)), int(round(theta.y))
    if abs(th_cos) == abs(th_sin):
        return
    x, y, z = int(x), int(y), int(z)
    x1, z1, x2, z2 = size
    u1 = - x1 * th_sin + x
    v1 = + x1 * th_cos + y
    w1 = z1 + z
    u2 = - x2 * th_sin + x
    v2 = + x2 * th_cos + y
    w2 = z2 + z
    u1, u2 = max(0, min(u1, u2)), min(511, max(u1, u2, 0))
    v1, v2 = max(0, min(v1, v2)), min(511, max(v1, v2, 0))
    w1, w2 = max(0, min(w1, w2) + 1), min(63, max(w1, w2))
    if value == DESTROY_BLOCK:
        clearbox.clear_solid(player.protocol, u1, v1, w1, u2, v2, w2, player.god)
    elif value == BUILD_BLOCK:
        buildbox.build_filled(player.protocol, u1, v1, w1, u2, v2, w2, player.color, player.god)


class CuboidState(state.BuildingState):
    ENTER_MESSAGE = S_PLANE
    EXIT_MESSAGE = S_PLANE_CANCEL

    def __init__(self, x1, x2, y1, y2):
        self.coordinates = (x1, x2, y1, y2)

    def on_block_removed(self, player, x, y, z):
        plane_operation(player, x, y, z, self.coordinates, DESTROY_BLOCK)

    def on_block_build(self, player, x, y, z):
        plane_operation(player, x, y, z, self.coordinates, BUILD_BLOCK)

    def on_line_build(self, player, points):
        for x, y, z in points:
            plane_operation(player, x, y, z, self.coordinates, BUILD_BLOCK)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    protocol, connection = state.apply_script(protocol, connection, config)

    return protocol, connection
