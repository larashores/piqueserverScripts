import click

from platforms import piqueargs


@piqueargs.group(usage='Usage: /platform [new name height freeze destroy last]')
def platform_command(connection):
    pass


@piqueargs.argument('label')
@platform_command.command(usage='Usage: /platform new <label>')
def new(connection, label):
    return 'new {}'.format(label)


@piqueargs.argument('label')
@platform_command.command(usage='Usage: /platform name <label>')
def name(connection, label):
    return 'name {}'.format(label)


@piqueargs.argument('height', type=click.INT)
@platform_command.command(usage='Usage: /platform height <height>')
def height(connection, height):
    return 'name {}'.format(height)


@platform_command.command(usage='Usage: /platform freeze')
def freeze(connection):
    return 'freeze'


@platform_command.command(usage='Usage: /platform destroy')
def destroy(connection):
    return 'destroy'


@platform_command.command(usage='Usage: /platform last')
def last(connection):
    pass


if __name__ == '__main__':
    result = platform_command.run('connection', [])
    print(result)

