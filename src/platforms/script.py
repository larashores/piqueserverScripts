"""
Platforms!

Just knowing the names of the four commands should be enough ingame,
as the parameter lists are provided when you try them.



/save
    Saves all platforms and button data to mapname_platform.txt
    Use SAVE_ON_MAP_CHANGE and AUTOSAVE_EVERY to avoid having to manually save.

/reach
    Increases your button activation reach. Meant to be used for getting rid
    of distance triggering buttons from a safe distance.

    Use again to revert to normal.

Maintainer: hompy
"""

# TODO
# Platforms 'freeze' when people spam the button
# Shoot trigger or destroy trigger (both?)
# Grenade launching action
# Prevent platforms from being hidden forever
# Negative heights
# Nicer way of having invisible buttons?
# Platforms crushing players
# Stop platforms action?

from platforms.util import piqueargs
from platforms.commands.buttoncommand import button
from platforms.commands.platformcommand import platform
from platforms.commands.triggercommand import trigger
from platforms.commands.actioncommand import action
from platforms.core.platformprotocol import platform_protocol
from platforms.core.platformconnection import platform_connection
from cbc.core import cbc


piqueargs.server_command(button, 'button', 'b')
piqueargs.server_command(platform, 'platform', 'p')
piqueargs.server_command(trigger, 'trigger', 'tr')
piqueargs.server_command(action, 'action', 'ac')


@piqueargs.command(usage=r'Usage: \save')
def save(connection):
    connection.protocol.dump_platform_json()
    return 'Platforms saved'


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    return platform_protocol(protocol), platform_connection(connection)
