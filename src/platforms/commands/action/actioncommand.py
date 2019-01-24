"""
/ac /action <command>
    Makes a button do something.

    command:
        add <action>
        set <action>
            Adds an action to the button. Set deletes all previous actions first,
            making the new action the only one.

            See /trigger for more information on who the "activating players" are.

            action:
                height   <height> [speed=0.15] [delay]
                raise    <amount> [speed=0.15] [delay]
                lower    <amount> [speed=0.15] [delay]
                elevator <height> [speed=0.25] [delay] [wait=3.0]
                    Speed determines how fast the platforms moves, in seconds.
                    Delay is the amount of time spent waiting before the platforms
                    actually starts to move.
                    Elevators can wait an amount of time at the end of the journey,
                    before heading back.
                output
                teleport <x y z|where>
                    Moves the activating players to the specified coordinates.
                    Using 'where' instead takes the last location where you stood
                    and executed the /where command.
                chat <text>
                    Sends text to the activating players.
                    You can put text between quotation marks to allow right
                    justifying with spaces, for example: "           Hello!"
                damage <amount>
                    Hits the activating players for that many hitpoints.
                    Use negative numbers to heal.
        list
            Lists the actions present in the button you select.

            Example:
            "Actions in 'mybutton': #0 platforms 'myplat' height(5) --
                #1 player teleport(16, 16, 32)"

            #0 and #1 are the action indexes to be used with /action del.
            'myplat' is the name of the platforms the height action is affecting,
            in this case making it 5 blocks tall.
        del <#|all>
            Delete a single action in a button by specifying its index. Action
            indexes can be looked up by using /action list.

            Negative indexes can be used too: -1 is the last added action, -2 the
            one before that, and so on.

            Specifying 'all' instead of a number erases all the actions.
"""
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
    return 'damage {}'.format(amount)


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
