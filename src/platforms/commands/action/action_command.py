from piqueserver.commands import command, join_arguments
from pyspades.constants import WEAPON_KILL, FALL_KILL

from platforms.parseargs import parseargs
from platforms.states.actionaddstate import ActionAddState
from platforms.states.actioncommandstate import ActionCommandState
from platforms.states.selectbuttonstate import SelectButtonState
from platforms.states.selectplatformstate import SelectPlatformState
from platforms.strings import *


S_ACTION_USAGE = 'Usage: /action <{commands}>'

ACTION_COMMAND_USAGES = {
    'add': 'Usage: /action add <{actions}>',
    'del': 'Usage: /action del <#|all>'
}
ACTION_COMMANDS = ('add', 'set', 'list', 'del')
ACTION_ADD_USAGES = {
    'height': 'Usage: /action add height <height> [speed=0.15] [delay]',
    'raise': 'Usage: /action add raise <amount> [speed=0.15] [delay]',
    'lower': 'Usage: /action add lower <amount> [speed=0.15] [delay]',
    'elevator': 'Usage: /action add elevator <height> [speed=0.25] [delay] [wait=3.0]',
    'output': 'Usage: /action add output [delay]',
    'teleport': 'Usage: /action add teleport <x y z|where>',
    'chat': 'Usage: /action add chat <text>',
    'damage': 'Usage: /action add damage <amount>',
}

@command('action', 'ac')
def action_command(connection, *args):
    protocol = connection.protocol
    if connection not in protocol.players:
        raise ValueError()
    player = connection
    state = player.states.top()

    if state:
        if state.get_parent().name == 'action' and not args:
            # cancel action command
            player.states.exit()
            return
        elif state.blocking:
            # can't switch from a blocking mode
            return S_EXIT_BLOCKING_STATE.format(state=state.name)

    available = '|'.join(ACTION_COMMANDS)
    usage = S_ACTION_USAGE.format(commands=available)
    try:
        command = args[0].lower()
        if command not in ACTION_COMMANDS:
            return usage

        if command in ('add', 'set'):
            add = command == 'add'
            available = '|'.join(ACTION_ADD_ACTIONS)
            usage = ACTION_COMMAND_USAGES['add'].format(actions=available)
            if not add:
                usage = usage.replace('add', 'set')

            action = args[1].lower()
            if action not in ACTION_ADD_ACTIONS:
                return usage

            usage = ACTION_ADD_USAGES.get(action, usage)
            if not add:
                usage = usage.replace('add', 'set')

            new_state = ActionAddState(action, add)
            new_states = [new_state, SelectButtonState(new_state)]
            if action in ('height', 'raise', 'lower', 'elevator'):
                kwargs = {}
                if action == 'elevator':
                    signature = 'int [float float float]'
                    value, speed, delay, wait = parseargs(signature, args[2:])
                    speed = 0.25 if speed is None else speed
                    kwargs['wait'] = 3.0 if wait is None else wait
                else:
                    signature = 'int [float float]'
                    value, speed, delay = parseargs(signature, args[2:])
                    speed = 0.15 if speed is None else speed
                kwargs['mode'] = action
                kwargs['height'] = value
                kwargs['speed'] = speed
                kwargs['delay'] = delay or 0.0
                # validate parameters
                for parameter, value in kwargs.items():
                    if type(value) in (int, float) and value < 0:
                        message = S_NOT_POSITIVE.format(parameter=parameter)
                        raise ValueError(message)
                new_state.kwargs = kwargs
                new_states.append(SelectPlatformState(new_state))
            elif action == 'output':
                delay, = parseargs('[float]', args[2:])
                new_state.kwargs = {
                    'mode': 'height',
                    'speed': 0.0,
                    'delay': delay or 0.0,
                    'force': True
                }
                new_states.append(SelectPlatformState(new_state))
            elif action == 'teleport':
                if join_arguments(args[2:]) == 'where':
                    if not player.where_location:
                        return S_WHERE_FIRST
                    x, y, z = player.where_location
                    x = round(x * 2.0) / 2.0 - 0.5
                    y = round(y * 2.0) / 2.0 - 0.5
                    z = round(z) + 0.5
                else:
                    x, y, z = parseargs('float float float', args[2:])
                if x <= 0.0 or x > 511.0:
                    raise ValueError(S_OUT_OF_BOUNDS.format(parameter='x'))
                if y <= 0.0 or y > 511.0:
                    raise ValueError(S_OUT_OF_BOUNDS.format(parameter='y'))
                if z <= 0.0 or z > 62.0:
                    raise ValueError(S_OUT_OF_BOUNDS_Z.format(parameter='z'))
                z = max(0.5, z)
                new_state.kwargs = {'location': (x, y, z)}
            elif action == 'chat':
                text = join_arguments(args[2:])
                if not text:
                    return usage
                new_state.kwargs = {'value': text}
            elif action == 'damage':
                amount, = parseargs('int', args[2:])
                damage_type = WEAPON_KILL if amount > 0 else FALL_KILL
                new_state.kwargs = {'value': amount, 'type': damage_type}
        else:
            usage = ACTION_COMMAND_USAGES.get(command, usage)
            new_state = ActionCommandState(command)
            new_states = [new_state, SelectButtonState(new_state)]
            if command == 'del':
                new_state.number, = parseargs('str', args[1:])
                if new_state.number != 'all':
                    new_state.number, = parseargs('int', args[1:])

        player.states.exit()
        for state in new_states[:-1]:
            player.states.push(state)
        player.states.enter(new_states[-1])
    except ValueError as err:
        player.send_chat(usage)
        return str(err)
    except IndexError:
        return usage
