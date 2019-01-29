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
                teleport <x y _z|where>
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
from pyspades.constants import WEAPON_KILL, FALL_KILL
from platforms import piqueargs
from platforms.strings import S_EXIT_BLOCKING_STATE, S_WHERE_FIRST
from platforms.states.action.actionstate import ActionState
from platforms.states.action.addactionstate import PlatformAddActionState, PlayerAddActionState, ActionType
from platforms.states.action.actioncommandstate import ActionListState, ActionDelState
from platforms.commands.util import IDENTIFIER

POS_FLOAT = piqueargs.FloatRange(0.0, 86400.0)


@piqueargs.group(usage='Usage: /action <add set list del>', required=False)
def action(connection, end=False):
    if not end:
        return

    if connection not in connection.protocol.players:
        raise ValueError()
    state = connection.state_stack.top()
    if state and isinstance(state.get_parent(), ActionState):
        connection.state_stack.exit()  # cancel action command
    elif state and state.blocking:
        return S_EXIT_BLOCKING_STATE.format(state=state.name)  # can't switch from a blocking mode


@action.group(usage='Usage: /action {} <height raise lower elevator teleport chat damage>',
              usageargs=['add'])
@piqueargs.pass_obj
def add(obj, connection):
    obj.clear_others = False


@action.group('set', usage='Usage: /action {} <height raise lower elevator teleport chat damage>',
              usageargs=['set'])
@piqueargs.pass_obj
def set_(obj, connection):
    obj.clear_others = True


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('height', type=piqueargs.IntRange(0, 62))
@piqueargs.command(usage='Usage: /action {} height <height> [speed=0.15] [delay]')
@piqueargs.pass_obj
def height(obj, connection, height, speed, delay):
    state = PlatformAddActionState(obj.clear_others, ActionType.HEIGHT, height, speed, delay)
    push_states(connection, [state])


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('amount', type=piqueargs.IntRange(0, 62))
@piqueargs.command('raise', usage='Usage: /action {} raise <amount> [speed=0.15] [delay]')
@piqueargs.pass_obj
def raise_(obj, connection, amount, speed, delay):
    state = PlatformAddActionState(obj.clear_others, ActionType.RAISE, amount, speed, delay)
    push_states(connection, [state])


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('amount', type=piqueargs.IntRange(0, 62))
@piqueargs.command(usage='Usage: /action {} lower <amount> [speed=0.15] [delay]')
@piqueargs.pass_obj
def lower(obj, connection, amount, speed, delay):
    state = PlatformAddActionState(obj.clear_others, ActionType.LOWER, lower, amount, speed, delay)
    push_states(connection, [state])


@piqueargs.argument('wait', default=3.0, type=POS_FLOAT, required=False)
@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('height', type=piqueargs.IntRange(0, 62))
@piqueargs.command(usage='Usage: /action {} elevator <height> [speed=0.25] [delay] [wait=3.0]')
@piqueargs.pass_obj
def elevator(obj, connection, height, speed, delay, wait):
    print(type(ActionType.ELEVATOR))
    state = PlatformAddActionState(obj.clear_others, ActionType.ELEVATOR, height, speed, delay, True, wait)
    push_states(connection, [state])


@piqueargs.argument('z', type=piqueargs.FloatRange(0.0, 62.0), required=False)
@piqueargs.argument('y', type=piqueargs.FloatRange(511.0, 511.0), required=False)
@piqueargs.argument('first')
@piqueargs.command(usage='Usage: /action {} teleport <x y _z|where>')
@piqueargs.pass_obj
def teleport(obj, connection, first, y, z):
    if first == 'where':
        if not connection.where_location:
            piqueargs.stop_parsing(S_WHERE_FIRST)
        x, y, z = connection.where_location
        x = round(x * 2.0) / 2.0 - 0.5
        y = round(y * 2.0) / 2.0 - 0.5
        z = round(z) + 0.5
    elif y is not None and z is not None:
        try:
            x = piqueargs.FloatRange.check_value('x', float(first), 0.0, 511.0)
        except ValueError:
            piqueargs.stop_parsing(teleport.usage)
    else:
        piqueargs.stop_parsing(teleport.usage)
    z = max(0.5, z)

    state = PlayerAddActionState(obj.clear_others, ActionType.TELEPORT, (x, y, z))
    push_states(connection, [state])


@piqueargs.argument('text')
@piqueargs.command(usage='Usage: /action {} chat <text>')
@piqueargs.pass_obj
def chat(obj, connection, text):
    state = PlayerAddActionState(obj.clear_others, ActionType.CHAT, text)
    push_states(connection, [state])


@piqueargs.argument('amount', type=piqueargs.IntRange(-100, 100))
@piqueargs.command(usage='Usage: /action {} damage <amount>')
@piqueargs.pass_obj
def damage(obj, connection, amount):
    state = PlayerAddActionState(obj.clear_others, ActionType.DAMAGE,
                                 kill_type=WEAPON_KILL if amount > 0 else FALL_KILL)
    push_states(connection, [state])


@action.command('list', usage='Usage: /action list')
def list_(connection):
    state = ActionListState()
    push_states(connection, [state])


@piqueargs.argument('what', type=IDENTIFIER)
@action.command('del', usage='Usage: /action del <#|all>')
def delete(connection, what):
    state = ActionDelState(what)
    push_states(connection, [state])


for command in (height, raise_, lower, elevator, teleport, chat, damage):
    add.add_command(command)
    set_.add_command(command)


def push_states(player, states):
    player.state_stack.clear()
    player.state_stack.push(*states)
