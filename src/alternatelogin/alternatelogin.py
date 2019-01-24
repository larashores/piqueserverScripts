"""
Creates an alternate system of logs in where each user has their own password and can belong to one or more groups.
Privileges are assigned on a group level instead of a per-user level. The special "admin" group is allowed to use every
command per the usual rules. Users can be updated on-the-fly with the passreload.py script. Passwords must be unique as
the usernames are not used to login with.

Config format:
############################################
    "users": {
    	"user1" : "password1",
    	"user2" : "password2",
        "user3" : "password3"
    },
    "usergroups": {
    	"admin": ["user1","user2"],
    	"mod": ["user3"]
    },
    "rights" : {
        "mod" : ["command1", "command2"]
    },
###########################################
"""

import commands


def login(connection, password):
    """
    Login into an account using only a unique password

    usage: \login password
    """
    if connection.username:
        return "You're already logged in as %s" % connection.username
    if connection not in connection.protocol.players:
        raise KeyError()
    for username, passwd in connection.protocol.users.iteritems():
        if password == passwd:
            connection.username = username
            return connection.on_user_login(username, True)
    if connection.login_retries is None:
        connection.login_retries = connection.protocol.login_retries - 1
    else:
        connection.login_retries -= 1
    if not connection.login_retries:
        connection.kick('Ran out of login attempts')
        return
    return 'Invalid password - you have %s tries left' % (
        connection.login_retries)
commands.add(login)


def whois(connection, player):
    """
    Gets the user that a player is logged in as

    usage: \whois playername
    """
    player = commands.get_player(connection.protocol, player)
    username = player.username
    if username is None:
        message = ' is not logged in.'
    else:
        message = ' is logged in as ' + username
    return player.name + message
commands.add(whois)


def apply_script(protocol, connection, config):
    class UserConnection(connection):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.username = None

        def on_user_login(self, username, verbose=True):
            user_groups = []
            for user_group, names in self.protocol.usergroups.iteritems():
                if username in names:
                    user_groups.append(user_group)
                    self.user_types.add(user_group)
                    if user_group == 'admin':
                        self.admin = True
                        self.speedhack_detect = False
                    rights = set(commands.rights.get(user_group, ()))
                    self.rights.update(rights)
            if verbose:
                message = ' logged in as %s' % username
                groups = ','.join(user_groups)
                self.send_chat('You' + message)
                self.send_chat('You are in usergroups: ' + groups)
                self.protocol.irc_say("* " + self.name + message)

    class UserProtocol(protocol):
        def __init__(self, *args, **kwargs):
            self.usergroups = config.get('usergroups', {})
            self.users = config.get('users', {})
            protocol.__init__(self, *args, **kwargs)

    return UserProtocol, UserConnection
