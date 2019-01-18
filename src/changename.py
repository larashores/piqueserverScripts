"""
Allows changing a players name mid game
"""

import commands

@commands.admin
def changename(connection, new_name, old_name=None):
    if old_name is None:
        old_name = connection.name
    try:
        player = commands.get_player(connection.protocol, old_name, False)
    except InvalidPlayer:
        return 'Invalid player'
    except InvalidSpectator:
        return 'Player is a spectator'
    msg = "Changed %s's name to %s" % (player.name, new_name)
    player.name = new_name
    return msg
commands.add(changename)


def apply_script(protocol, connection, config):
    return protocol, connection
