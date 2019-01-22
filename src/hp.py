"""
Get and set a player's hp!

/hp <player name or id>

Author: infogulch
"""

from piqueserver.commands import command, get_player


@command("hp")
def hp(connection, name=None):
    if name is not None:
        player = get_player(connection.protocol, name)
    else:
        player = connection
    if player not in player.protocol.players:
        raise ValueError()
    return "{}'s HP is: {}".format(player.name, player.hp)


def apply_script(protocol, connection, config):
    return protocol, connection
