import click
from platforms import piqueargs


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
