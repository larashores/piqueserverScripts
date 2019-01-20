"""
Allows changing another's fly status only if admin
"""

from piqueserver.commands import command, get_player


@command('fly')
def fly(connection, player=None):
    protocol = connection.protocol
    if player is not None:
        if connection.admin:
            player = get_player(connection.protocol, player)
        else:
            return 'No administrator rights!'
    elif connection in protocol.players:
        player = connection
    else:
        raise ValueError('Invalid player')
    player.fly = not player.fly

    message = 'now flying' if player.fly else 'no longer flying'
    player.send_chat("You're {}".format(message))
    if connection is not player and connection in protocol.players:
        connection.send_chat('{} is {}'.format(player.name, message))
    protocol.send_chat('{} is {}'.format(player.name, message), irc=True)


def apply_script(protocol, connection, config):
    return protocol, connection
