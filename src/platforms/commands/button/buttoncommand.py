import click

from platforms import piqueargs


@piqueargs.group(usage="Usage: /button [new name destroy toggle cooldown last]")
def button_command(connection):
    pass


@piqueargs.argument('label')
@button_command.command(usage='Usage: /button new <label>')
def new(connection, label):
    return 'new {}'.format(label)


@piqueargs.argument('label')
@button_command.command(usage='Usage: /button name <label>')
def name(connection, label):
    return 'name {}'.format(label)


@piqueargs.argument('seconds', type=click.INT)
@button_command.command(usage='Usage: /button cooldown <seconds>')
def cooldown(connection, seconds):
    return 'cooldown {}'.format(seconds)


@button_command.command(usage='Usage: /button destroy')
def destroy(connection):
    return 'destroy'


@button_command.command(usage='Usage: /button last')
def last(connection):
    return 'last'


if __name__ == '__main__':
    result = button_command.run('button_command', [])
    print(result)
