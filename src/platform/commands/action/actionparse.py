import click
from platform import piqueargs


@piqueargs.group(usage='Usage: /action <{commands}>')
def action(connection):
    pass


@action.group(usage='Usage: /action add <{actions}>')
def add(connection):
    pass


@action.group('set', usage='Usage: /action set <{actions}>')
def set_(connection):
    pass


@click.argument('delay', default=0.0, type=click.FLOAT, required=False)
@click.argument('speed', default=.15, type=click.FLOAT, required=False)
@click.argument('height', type=click.FLOAT)
@piqueargs.command(usage='Usage: /action add height <height> [speed=0.15] [delay]')
def height(connection, height, speed, delay):
    return 'height {} {} {}'.format(height, speed, delay)


@click.argument('delay', default=0.0, type=click.FLOAT, required=False)
@click.argument('speed', default=.15, type=click.FLOAT, required=False)
@click.argument('amount', type=click.FLOAT)
@piqueargs.command('raise', usage='Usage: /action add raise <amount> [speed=0.15] [delay]')
def raise_(connection, amount, speed, delay):
    return 'raise {} {} {}'.format(amount, speed, delay)


@click.argument('delay', default=0.0, type=click.FLOAT, required=False)
@click.argument('speed', default=.15, type=click.FLOAT, required=False)
@click.argument('amount', type=click.FLOAT)
@piqueargs.command(usage='Usage: /action add lower <amount> [speed=0.15] [delay]')
def lower(connection, amount, speed, delay):
    return 'lower {} {} {}'.format(amount, speed, delay)


@click.argument('wait', default=3.0, type=click.FLOAT, required=False)
@click.argument('delay', default=0.0, type=click.FLOAT, required=False)
@click.argument('speed', default=.15, type=click.FLOAT, required=False)
@click.argument('height', type=click.FLOAT)
@piqueargs.command(usage='Usage: /action add elevator <height> [speed=0.25] [delay] [wait=3.0]')
def elevator(connection, height, speed, delay, wait):
    return 'elevator {} {} {} {}'.format(height, speed, delay, wait)


@piqueargs.command(usage='Usage: /action add output [delay]')
def output(connection):
    return 'output'


@piqueargs.command(usage='Usage: /action add teleport <x y z|where>')
def teleport(connection):
    return 'teleport'


@click.argument('text')
@piqueargs.command(usage='Usage: /action add chat <text>')
def chat(connection, text):
    return 'chat {}'.format(text)


@click.argument('amount', type=click.INT)
@piqueargs.command(usage='Usage: /action add damage <amount>')
def damage(connection, amount):
    return '{}: damage {}'.format(connection, amount)


@action.command('list', usage='Usage: /action list')
def list_(connection):
    return 'list'


@click.argument('z', type=click.INT, required=False)
@click.argument('y', type=click.INT, required=False)
@click.argument('first')
@action.command('del', usage='Usage: /action del <#|all>')
def delete(connection, first, y, z):
    if first == 'where':
        return 'delete where'
    elif y is not None and z is not None:
        try:
            return 'delete {} {} {}'.format(int(first), y, z)
        except ValueError:
            piqueargs.bad_command(delete.usage)
    else:
        piqueargs.bad_command(delete.usage)


add_set_commands = [
    height,
    raise_,
    lower,
    elevator,
    output,
    teleport,
    chat,
    damage
]
for command in add_set_commands:
    add.add_command(command)
    set_.add_command(command)


if __name__ == '__main__':
    result = action.run('hello', ['add', 'damage', '3'])
    print(result)
