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

from platforms import piqueargs
from platforms.core.platformconnection import platform_connection
from platforms.core.platformprotocol import platform_protocol
from platforms.commands.actioncommand import action
from platforms.commands.buttoncommand import button
from platforms.commands.platformcommand import platform
from platforms.commands.triggercommand import trigger
from platforms.commands.commands import save, reach


piqueargs.add_server_command(action, 'action', 'ac')
piqueargs.add_server_command(button, 'button', 'b')
piqueargs.add_server_command(platform, 'action', 'p')
piqueargs.add_server_command(trigger, 'trigger', 'tr')
piqueargs.add_server_command(save)
piqueargs.add_server_command(reach)


def apply_script(protocol, connection, config):
    return platform_protocol(protocol), platform_connection(connection)
