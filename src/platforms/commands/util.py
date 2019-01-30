import click
from platforms.util import piqueargs


def base_command(connection, end, state_type, usage_message):
    if not end:
        return
    if connection not in connection.protocol.players:
        raise ValueError()
    if isinstance(connection.state_stack.top(), state_type):
        connection.state_stack.exit()  # cancel command
        return
    return usage_message


class _Identifier(click.ParamType):
    name = 'platform'

    def convert(self, value, param, ctx):
        if value == 'all':
            return value
        try:
            return int(value)
        except ValueError:
            piqueargs.stop_parsing(param.usage)
        piqueargs.stop_parsing(param.usage)


IDENTIFIER = _Identifier()
