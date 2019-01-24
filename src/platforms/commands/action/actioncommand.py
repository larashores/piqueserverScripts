import click

from platforms import piqueargs


@piqueargs.group(usage='Usage: /action <add set list del>')
def action(connection):
    pass


@action.group(usage='Usage: /action {} <height raise lower elevator output teleport chat damage>', usageargs=['add'])
def add(connection):
    pass


@action.group('set', usage='Usage: /action {} <height raise lower elevator output teleport chat damage>', usageargs=['set'])
def set_(connection):
    pass


@piqueargs.argument('delay', default=0.0, type=click.FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=click.FLOAT, required=False)
@piqueargs.argument('height', type=click.FLOAT)
@piqueargs.command(usage='Usage: /action {} height <height> [speed=0.15] [delay]')
def height(connection, height, speed, delay):
    return 'height {} {} {}'.format(height, speed, delay)


@piqueargs.argument('delay', default=0.0, type=click.FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=click.FLOAT, required=False)
@piqueargs.argument('amount', type=click.FLOAT)
@piqueargs.command('raise', usage='Usage: /action {} raise <amount> [speed=0.15] [delay]')
def raise_(connection, amount, speed, delay):
    return 'raise {} {} {}'.format(amount, speed, delay)


@piqueargs.argument('delay', default=0.0, type=click.FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=click.FLOAT, required=False)
@piqueargs.argument('amount', type=click.FLOAT)
@piqueargs.command(usage='Usage: /action {} lower <amount> [speed=0.15] [delay]')
def lower(connection, amount, speed, delay):
    return 'lower {} {} {}'.format(amount, speed, delay)


@piqueargs.argument('wait', default=3.0, type=click.FLOAT, required=False)
@piqueargs.argument('delay', default=0.0, type=click.FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=click.FLOAT, required=False)
@piqueargs.argument('height', type=click.FLOAT)
@piqueargs.command(usage='Usage: /action {} elevator <height> [speed=0.25] [delay] [wait=3.0]')
def elevator(connection, height, speed, delay, wait):
    return 'elevator {} {} {} {}'.format(height, speed, delay, wait)


@piqueargs.command(usage='Usage: /action {} output [delay]')
def output(connection):
    return 'output'


@piqueargs.argument('z', type=click.INT, required=False)
@piqueargs.argument('y', type=click.INT, required=False)
@piqueargs.argument('first')
@piqueargs.command(usage='Usage: /action {} teleport <x y z|where>')
def teleport(connection, first, y, z):
    if first == 'where':
        return 'teleport where'
    elif y is not None and z is not None:
        try:
            return 'teleport {} {} {}'.format(int(first), y, z)
        except ValueError:
            piqueargs.bad_command(teleport.usage)
    else:
        piqueargs.bad_command(teleport.usage)


@piqueargs.argument('text')
@piqueargs.command(usage='Usage: /action {} chat <text>')
def chat(connection, text):
    return 'chat {}'.format(text)


@piqueargs.argument('amount', type=click.INT)
@piqueargs.command(usage='Usage: /action {} damage <amount>')
def damage(connection, amount):
    return '{}: damage {}'.format(connection, amount)


@action.command('list', usage='Usage: /action list')
def list_(connection):
    return 'list'


@piqueargs.argument('what')
@action.command('del', usage='Usage: /action del <#|all>')
def delete(connection, what):
    if what == 'all':
        return 'delete all'
    else:
        try:
            what = int(what)
        except ValueError:
            piqueargs.bad_command(delete.usage)
    return 'delete {}'.format(what)


for command in (height, raise_, lower, elevator, output, teleport, chat, damage):
    add.add_command(command)
    set_.add_command(command)


if __name__ == '__main__':
    result = action.run('connection', [])
    print(result)
