from piqueserver.commands import command, get_player


@command("setlocation")
def set_location(connection, x, y, z):
    connection.set_location_safe((int(x), int(y), int(z)))


@command("getlocation")
def get_location(connection, name=None):
    if name is not None:
        player = get_player(connection.protocol, name)
    else:
        player = connection
    if player not in player.protocol.players:
        raise ValueError()
    position = connection.world_object.position
    x, y, z = position.x, position.y, position.z
    return '{} is at position ({}, {}, {})'.format(player.name, int(x), int(y), int(z))


def apply_script(protocol, connection, config):
    return protocol, connection
