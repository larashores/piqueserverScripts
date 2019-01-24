import click

from platforms import piqueargs


@piqueargs.group(usage='Usage: /trigger add set list del logic quiet')
def triggercommand(connection):
    pass


@piqueargs.option('not', 'notarg')
@triggercommand.group(usage='Usage: /action {} [not] <press distance track height>', usageargs=['add'])
def add(connection, notarg):
    print('add{}'.format(' not' if notarg else ''))


@piqueargs.option('not', 'notarg')
@triggercommand.group('set', usage='Usage: /action {} [not] <press distance track height>>', usageargs=['set'])
def set_(connection, notarg):
    print('set{}'.format(' not' if notarg else ''))


@piqueargs.command(usage='Usage: /action {} [not] press')
def press(connection):
    return 'press'


@piqueargs.argument('radius', default=3.0, type=click.FLOAT, required=False)
@piqueargs.command('raise', usage='Usage: /trigger {} [not] distance [radius=3]')
def distance(connection, radius):
    return 'distance {}'.format(radius)


@piqueargs.argument('radius', default=3.0, type=click.FLOAT, required=False)
@piqueargs.command(usage='Usage: /trigger {} [not] track [radius=3]')
def track(connection, radius):
    return 'track {}'.format(radius)


@piqueargs.argument('height', type=click.INT)
@piqueargs.command(usage='/trigger {} [not] height <height>')
def height(connection, height):
    return 'height {}'.format(height)


@triggercommand.command('list', usage='Usage: /trigger list')
def list_(connection):
    return 'list'


@piqueargs.argument('what')
@triggercommand.command('del', usage='Usage: /trigger del <#|all>')
def delete(connection, what):
    return 'delete {}'.format(what)


@piqueargs.argument('andor')
@triggercommand.command(usage='Usage: /trigger logic <and|or>')
def logic(connection, andor):
    return 'logic {}'.format(andor)


@triggercommand.command(usage='Usage: /trigger quiet')
def quiet(connection):
    return 'quiet'


for command in (press, distance, track, height):
    add.add_command(command)
    set_.add_command(command)


if __name__ == '__main__':
    result = triggercommand.run('connection', [])
    print(result)
