import builtins
from pyspades.constants import *
from piqueserver.commands import command
from cbc.core import buildbox, clearbox, cbc

S_PLANE_USAGE = 'Usage: /plane <-x> <+x> <-y> <+y>'
S_PLANE_CANCEL = 'No longer plane-building'
S_PLANE = 'Dig or build to make or remove slabs, with the block as center. ' \
    'Abort with /plane'
S_TOO_MANY_PARAMETERS = 'ERROR: too many parameters'
S_NOT_ENOUGH_PARAMETERS = 'ERROR: not enough parameters'
S_WRONG_PARAMETER_TYPE = 'ERROR: wrong parameter type'


def parseargs(signature, args):
    signature = signature.split()
    if len(args) > len(signature):
        raise ValueError(S_TOO_MANY_PARAMETERS)
    result = []
    optional = False
    for i, type_desc in enumerate(signature):
        type_name = type_desc.strip('[]')
        optional = optional or type_name != type_desc
        try:
            typecast = getattr(builtins, type_name)
            result.append(typecast(args[i]))
        except ValueError:
            raise ValueError(S_WRONG_PARAMETER_TYPE)
        except IndexError:
            if not optional:
                raise ValueError(S_NOT_ENOUGH_PARAMETERS)
            result.append(None)
    return result


@command('plane')
def plane(connection, *args):
    protocol = connection.protocol
    if connection not in protocol.players:
        raise ValueError()
    player = connection

    if player.plane_coordinates and not args:
        player.plane_coordinates = None
        return S_PLANE_CANCEL
    try:
        x1, x2, y1, y2 = parseargs('int int int int', args)
        connection.plane_coordinates = (x1, y1, x2, y2)
        return S_PLANE
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
    y1, y2 = 0, 0
    u1 = y1 * th_cos - x1 * th_sin + x
    v1 = y1 * th_sin + x1 * th_cos + y
    w1 = z1 + z
    u2 = y2 * th_cos - x2 * th_sin + x
    v2 = y2 * th_sin + x2 * th_cos + y
    w2 = z2 + z
    u1, u2 = max(0, min(u1, u2)), min(511, max(u1, u2, 0) + 1)
    v1, v2 = max(0, min(v1, v2)), min(511, max(v1, v2, 0) + 1)
    w1, w2 = max(0, min(w1, w2) + 1), min(63, max(w1, w2) + 1)
    if value == DESTROY_BLOCK:
        clearbox.clear_solid(player.protocol, u1, v1, w1, u2-1, v2-1, w2-1, player.god)
    elif value == BUILD_BLOCK:
        buildbox.build_filled(player.protocol, u1, v1, w1, u2-1, v2-1, w2-1, player.color, player.god)


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)

    class CuboidConnection(connection):
        def __init__(self, *args, **kwargs):
            self.plane_coordinates = None
            connection.__init__(self, *args, **kwargs)

        def on_reset(self):
            self.plane_coordinates = None
            connection.on_reset(self)

        def on_login(self, name):
            self.plane_coordinates = None
            connection.on_login(self, name)

        def on_disconnect(self):
            self.plane_coordinates = None
            connection.on_disconnect(self)

        def on_block_removed(self, x, y, z):
            if self.plane_coordinates:
                plane_operation(self, x, y, z, self.plane_coordinates, DESTROY_BLOCK)
            connection.on_block_removed(self, x, y, z)

        def on_block_build(self, x, y, z):
            if self.plane_coordinates:
                plane_operation(self, x, y, z, self.plane_coordinates, BUILD_BLOCK)
            connection.on_block_build(self, x, y, z)

        def on_line_build(self, points):
            if self.plane_coordinates:
                for x, y, z in points:
                    plane_operation(self, x, y, z, self.plane_coordinates, BUILD_BLOCK)
            connection.on_line_build(self, points)

    return protocol, CuboidConnection
