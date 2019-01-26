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
from pyspades.constants import WEAPON_KILL, FALL_KILL
from platforms import piqueargs
from platforms.strings import S_EXIT_BLOCKING_STATE, S_WHERE_FIRST
from platforms.states.action.actionaddstate import ActionAddState
from platforms.states.action.actioncommandstate import ActionCommandState
from platforms.states.button.selectbuttonstate import SelectButtonState
from platforms.states.platform.selectplatformstate import SelectPlatformState
from platforms.worldobjects.action.platformaction import PlatformActionType
from platforms.worldobjects.action.playeraction import PlayerActionType
from platforms.commands.util import IDENTIFIER

POS_FLOAT = piqueargs.FloatRange(0.0, 86400.0)


@piqueargs.group(usage='Usage: /action <add set list del>', required=False)
def action(connection, end=False):
    if not end:
        return

    if connection not in connection.protocol.players:
        raise ValueError()
    state = connection.states.top()
    if state and state.get_parent().name == 'action':
        connection.states.exit()  # cancel action command
    elif state and state.blocking:
        return S_EXIT_BLOCKING_STATE.format(state=state.name)  # can't switch from a blocking mode


@action.group(usage='Usage: /action {} <height raise lower elevator output teleport chat damage>', usageargs=['add'])
@piqueargs.pass_obj
def add(obj, connection):
    obj.add = True


@action.group('set', usage='Usage: /action {} <height raise lower elevator output teleport chat damage>', usageargs=['set'])
@piqueargs.pass_obj
def set_(obj, connection):
    obj.add = False


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('height', type=POS_FLOAT)
@piqueargs.command(usage='Usage: /action {} height <height> [speed=0.15] [delay]')
@piqueargs.pass_obj
def height(obj, connection, height, speed, delay):
    state = ActionAddState(PlatformActionType.HEIGHT,
                           obj.add, mode='elevator', height=height, speed=speed, delay=delay)
    push_states(connection, [state, SelectButtonState(state), SelectPlatformState(state)])


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('amount', type=POS_FLOAT)
@piqueargs.command('raise', usage='Usage: /action {} raise <amount> [speed=0.15] [delay]')
@piqueargs.pass_obj
def raise_(obj, connection, amount, speed, delay):
    state = ActionAddState(PlatformActionType.RAISE,
                           obj.add, mode='raise', amount=amount, speed=speed, delay=delay)
    push_states(connection, [state, SelectButtonState(state), SelectPlatformState(state)])


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('amount', type=POS_FLOAT)
@piqueargs.command(usage='Usage: /action {} lower <amount> [speed=0.15] [delay]')
@piqueargs.pass_obj
def lower(obj, connection, amount, speed, delay):
    state = ActionAddState(PlatformActionType.LOWER,
                           obj.add, mode='lower', lower=lower, amount=amount, speed=speed, delay=delay)
    push_states(connection, [state, SelectButtonState(state), SelectPlatformState(state)])


@piqueargs.argument('wait', default=3.0, type=POS_FLOAT, required=False)
@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('height', type=POS_FLOAT)
@piqueargs.command(usage='Usage: /action {} elevator <height> [speed=0.25] [delay] [wait=3.0]')
@piqueargs.pass_obj
def elevator(obj, connection, height, speed, delay, wait):
    state = ActionAddState(PlatformActionType.ELEVATOR,
                           obj.add, mode='elevator', height=height, speed=speed, delay=delay, wait='wait')
    push_states(connection, [state, SelectButtonState(state), SelectPlatformState(state)])


@piqueargs.argument('delay', type=piqueargs.FloatRange())
@piqueargs.command(usage='Usage: /action {} output [delay]')
@piqueargs.pass_obj
def output(obj, connection, delay):
    state = ActionAddState(PlatformActionType.OUTPUT,
                           obj.add, mode='height', speed=0.0, delay=delay or 0.0, force=True)
    push_states(connection, [state, SelectButtonState(state), SelectPlatformState(state)])


@piqueargs.argument('z', type=piqueargs.FloatRange(0.0, 62.0), required=False)
@piqueargs.argument('y', type=piqueargs.FloatRange(511.0, 511.0), required=False)
@piqueargs.argument('first')
@piqueargs.command(usage='Usage: /action {} teleport <x y z|where>')
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

    state = ActionAddState(PlayerActionType.TELEPORT, obj.add, location=(x, y, z))
    push_states(connection, [state, SelectButtonState(state)])


@piqueargs.argument('text')
@piqueargs.command(usage='Usage: /action {} chat <text>')
@piqueargs.pass_obj
def chat(obj, connection, text):
    state = ActionAddState(PlayerActionType.CHAT, obj.add, value=text)
    push_states(connection, [state, SelectButtonState(state)])


@piqueargs.argument('amount', type=piqueargs.IntRange(-100, 100))
@piqueargs.command(usage='Usage: /action {} damage <amount>')
@piqueargs.pass_obj
def damage(obj, connection, amount):
    state = ActionAddState(PlayerActionType.DAMAGE,
                           obj.add, value=amount, type=WEAPON_KILL if amount > 0 else FALL_KILL,)
    state.kwargs = {'value': amount, 'type': WEAPON_KILL if amount > 0 else FALL_KILL}
    push_states(connection, [state, SelectButtonState(state)])
    return 'damage {}'.format(amount)


@action.command('list', usage='Usage: /action list')
def list_(connection):
    state = ActionCommandState('list')
    push_states(connection, [state, SelectButtonState(state)])


@piqueargs.argument('what', type=IDENTIFIER)
@action.command('del', usage='Usage: /action del <#|all>')
def delete(connection, what):
    state = ActionCommandState('del')
    state.number = what
    push_states(connection, [state, SelectButtonState(state)])


for command in (height, raise_, lower, elevator, output, teleport, chat, damage):
    add.add_command(command)
    set_.add_command(command)


def push_states(player, states):
    player.states.exit()
    for state in states[:-1]:
        player.states.push(state)
    player.states.enter(states[-1])
