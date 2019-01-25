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
from platforms.strings import S_EXIT_BLOCKING_STATE, S_WHERE_FIRST
from platforms.states.triggeraddstate import TriggerAddState
from platforms.states.triggercommandstate import TriggerCommandState
from platforms.states.selectbuttonstate import SelectButtonState
from platforms.states.selectplatformstate import SelectPlatformState

POS_FLOAT = piqueargs.FloatRange(0.0, 64.0)


@piqueargs.group(usage='Usage: /trigger add set list del logic quiet', require=True)
@piqueargs.pass_obj
def triggercommand(connection, end=False):
    if not end:
        return

    if connection not in connection.protocol.players:
        raise ValueError()
    state = connection.states.top()
    if state and state.get_parent().name == 'trigger':
        connection.states.exit()  # cancel action command
    elif state and state.blocking:
        return S_EXIT_BLOCKING_STATE.format(state=state.name)  # can't switch from a blocking mode


@piqueargs.option('not', 'notarg')
@triggercommand.group(usage='Usage: /trigger {} [not] <press distance track height>', usageargs=['add'])
@piqueargs.pass_obj
def add(obj, connection, notarg):
    obj.add = True
    obj.notarg = notarg


@piqueargs.option('not', 'notarg')
@triggercommand.group('set', usage='Usage: /trigger {} [not] <press distance track height>>', usageargs=['set'])
@piqueargs.pass_obj
def set_(obj, connection, notarg):
    obj.add = False
    obj.notarg = notarg


@piqueargs.command(usage='Usage: /trigger {} [not] press')
@piqueargs.pass_obj
def press(obj, connection):
    state = TriggerAddState('press', obj.negate, obj.add)
    push_states(connection, [state, SelectButtonState(state)])


@piqueargs.argument('radius', default=3.0, type=POS_FLOAT, required=False)
@piqueargs.command('raise', usage='Usage: /trigger {} [not] distance [radius=3]')
@piqueargs.pass_obj
def distance(obj, connection, radius):
    state = TriggerAddState('distance', obj.negate, obj.add)
    state.radius = radius
    push_states(connection, [state, SelectButtonState(state)])


@piqueargs.argument('radius', default=3.0, type=POS_FLOAT, required=False)
@piqueargs.command(usage='Usage: /trigger {} [not] track [radius=3]')
@piqueargs.pass_obj
def track(obj, connection, radius):
    state = TriggerAddState('track', obj.negate, obj.add)
    state.radius = radius
    push_states(connection, [state, SelectButtonState(state)])


@piqueargs.argument('height', type=piqueargs.IntRange(0, 62))
@piqueargs.command(usage='/trigger {} [not] height <height>')
@piqueargs.pass_obj
def height(obj, connection, height):
    state = TriggerAddState('height', obj.negate, obj.add)
    state.height = height
    push_states(connection, [state, SelectButtonState(state), SelectPlatformState(state)])


@triggercommand.command('list', usage='Usage: /trigger list')
def list_(connection):
    state = TriggerCommandState('list')
    push_states(connection, [state, SelectButtonState(state)])


@piqueargs.argument('what')
@triggercommand.command('del', usage='Usage: /trigger del <#|all>')
def delete(connection, what):
    state = TriggerCommandState('del')
    if what == 'all':
        state.number = what
    else:
        try:
            state.number = int(what)
        except ValueError:
            piqueargs.stop_parsing(delete.usage)
        piqueargs.stop_parsing(delete.usage)
    push_states(connection, [state, SelectButtonState(state)])


@piqueargs.argument('andor', type=click.Choice('and', 'or'))
@triggercommand.command(usage='Usage: /trigger logic <and|or>')
def logic(connection, andor):
    state = TriggerCommandState('logic')
    state.logic = andor
    push_states(connection, [state, SelectButtonState(state)])


@triggercommand.command(usage='Usage: /trigger quiet')
def quiet(connection):
    state = TriggerCommandState('quiet')
    push_states(connection, [state, SelectButtonState(state)])


for command in (press, distance, track, height):
    add.add_command(command)
    set_.add_command(command)


def push_states(player, states):
    player.states.exit()
    for state in states[:-1]:
        player.states.push(state)
    player.states.enter(states[-1])
