"""
Redefines god to build mode, and only allows changing other's build status if admin. Only blue team can be build mode
unless build mode set with /fb
"""

from piqueserver.commands import command, get_player


@command('buildmode', 'bm')
def god(connection, name=None):
    if name is not None:
        if not connection.admin:
            return 'No administrator rights!'
        player = get_player(connection.protocol, name)
    else:
        player = connection
    if player not in player.protocol.players:
        raise ValueError()
    player.infinite_blocks = False
    player.god = not player.god
    if player.god:
        message = '{} entered BUILD MODE!'
        player.set_team(player.protocol.blue_team)
        player.respawn_time = 0
    else:
        message = '{} returned to being a mere sightseer'
        player.set_team(player.protocol.green_team)
        player.respawn_time = player.protocol.respawn_time
    player.protocol.send_chat(message.format(connection.name), irc=True)


@command('forcebuild', 'fb')
def force_build(connection):
    if connection not in connection.protocol.players:
        raise ValueError()
    connection.infinite_blocks = False
    connection.god = not connection.god
    message = "You've entered build mode" if connection.god else "You've exited build mode"
    connection.send_chat(message)


def apply_script(protocol, connection, config):

    class BuildModeConnection(connection):
        def on_hit(self, hit_amount, player, type, grenade):
            def check_god(check_player, msg):
                if check_player.god:
                    if not player.invisible:
                        self.send_chat(msg)
                    return False
                return True
            if not check_god(self, "You can't hurt people while you are in *Build Mode*"):
                return False
            if not check_god(player, "You can't hurt %s! That player is in *Build Mode*" % player.name):
                return False
            return connection.on_hit(self, hit_amount, player, type, grenade)

        def on_team_join(self, team):
            connection.on_team_join(self, team)
            if self.team == self.protocol.green_team:
                if self.god:
                    self.god = False
                    message = '%s returned to being a mere sightseer'
                    self.protocol.send_chat(message % connection.name)

    return protocol, BuildModeConnection
