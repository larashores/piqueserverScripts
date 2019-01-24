"""
/t /trigger <command>
    Triggers are what makes a button know when to act and when not to.

    command:
        add [not] <action>
        set [not] <action>
            Adds a trigger to the button. Set deletes all previous triggers first,
            making the new trigger the only one.

            Putting 'not' before the action makes it NEGATE the output.
            If you want to make a button that activates when a player *leaves*
            a zone, you could use "/trigger set not distance 5"

            action:
                press
                    Fires when a player normally hits the button with the spade.
                distance [radius=3]
                    True when a player gets within <radius> blocks of the
                    button (note: box distance, not sphere).
                track [radius=3]
                    Same as distance, but tracks one player and only one player.

                    Useful for creating a button that requires a specific number
                    of nearby players.
                height <height>
                    True when the platforms is exactly the specified height.
        list
            Lists the triggers present in the button you select.

            Example:
            "Triggers in 'mybutton': #0 player press OR #1 player distance=5 [CHECK]"

            #0 and #1 are the trigger indexes to be used with /trigger del.
            [CHECK] means the trigger currently yields true. The player in this
            case is near the button, but hasn't pressed it.

            This button uses OR logic, meaning that EITHER of these triggers
            firing is enough to activate the button.
        del <#|all>
            Delete a single trigger in a button by specifying its index. Trigger
            indexes can be looked up by using /trigger list.

            Negative indexes can be used too: -1 is the last added trigger, -2 the
            one before that, and so on.

            Specifying 'all' instead of a number erases all the triggers.
        logic <and|or>
            "AND" will make the button activate when ALL its triggers yield true.
            "OR" will make the button activate when ANY of its triggers fire.
        quiet
            Makes a button either become silent or resume playing animation and
            sound when it activates.
"""

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
