"""
Starts build mode for build server. Protects areas, changes team names and locks
builder team.
"""
from pyspades.common import coordinates
from pyspades.constants import CTF_MODE
from piqueserver.commands import command

DONT_PROTECT = ['g7', 'g8', 'h7', ' h8']


@command('protectall')
def protect_all(connection):
    connection.protocol.protect_all()
    connection.send_chat('Build areas protected')


def apply_script(protocol, connection, config):
    class BuildProtocol(protocol):
        game_mode = CTF_MODE

        def __init__(self, *args, **kwargs):
            protocol.__init__(self, *args, **kwargs)
            self.blue_team.locked = True
            self.blue_team.name = 'Builders'
            self.green_team.name = 'Others'
            self.protect_all()

        def set_map(self, map_obj):
            result = protocol.on_map_change(self, map_obj)
            self.protect_all()
            return result

        def protect_all(self):
            self.protected = set()
            for letter in 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h':
                for num in range(8):
                    grid = letter+str(num+1)
                    if grid not in DONT_PROTECT:
                        pos = coordinates(grid)
                        self.protected.symmetric_difference_update([pos])

    return BuildProtocol, connection
