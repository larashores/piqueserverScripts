"""
originally written by Danke

Modified to be compatible with alternatelogin.py script and the defaultcommands script
"""

import commands
import json

from pyspades.types import AttributeSet


@commands.admin
def reloadconfig(connection):
    new_config = {}
    try:
        new_config.update(json.load(open('config.txt', 'r')))
        if not isinstance(new_config, dict):
            raise ValueError('config.txt is not a mapping type')
    except ValueError, v:
        return 'Error reloading config. Check pyspades log for details.'
    connection.protocol.config.update(new_config)
    connection.protocol.reload_passes()
    return 'Config reloaded!'
commands.add(reloadconfig)


def apply_script(protocol, connection, config):
    class PassreloadProtocol(protocol):
        def reload_passes(self):
            self.users = config.get('users', {})
            self.usergroups = config.get('usergroups', {})
            self.defaultcommands = config.get('defaultcommands', {})
            for password in self.passwords.get('admin', []):
                if not password:
                    self.everyone_is_admin = True
            commands.rights.update(config.get('rights', {}))
            for connection in self.connections.values():
                connection.rights = AttributeSet()
                name = connection.username
                if name is None:
                    continue
                if name in self.users.keys():
                    connection.on_user_login(name, True)
                else:
                    connection.username = None
                    connection.send_chat('You have been logged out. Your account name has changed or been deleted.')

    return PassreloadProtocol, connection
