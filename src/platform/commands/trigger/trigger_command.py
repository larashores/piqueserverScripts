from piqueserver.commands import command

S_TRIGGER_USAGE = 'Usage: /trigger <{commands}>'

@command('trigger', 't')
def trigger_command(connection, *args):
    protocol = connection.protocol
    if connection not in protocol.players:
        raise ValueError()
    player = connection
    state = player.states.top()

    if state:
        if state.get_parent().name == 'trigger' and not args:
            # cancel trigger command
            player.states.exit()
            return
        elif state.blocking:
            # can't switch from a blocking mode
            return S_EXIT_BLOCKING_STATE.format(state = state.name)

    available = '|'.join(TRIGGER_COMMANDS)
    usage = S_TRIGGER_USAGE.format(commands = available)
    try:
        command = args[0].lower()
        if command not in TRIGGER_COMMANDS:
            return usage

        if command in ('add', 'set'):
            add = command == 'add'
            available = '|'.join(TRIGGER_ADD_TRIGGERS)
            usage = S_TRIGGER_ADD_USAGE.format(triggers = available)
            if not add:
                usage = usage.replace('add', 'set')

            negate = args[1].lower() == 'not'
            if negate:
                args = args[:1] + args[2:]

            trigger = args[1].lower()
            if trigger not in TRIGGER_ADD_TRIGGERS:
                return usage

            usage = TRIGGER_ADD_USAGES.get(trigger, usage)
            if not add:
                usage = usage.replace('add', 'set')

            new_state = TriggerAddState(trigger, negate, add)
            new_states = [new_state, SelectButtonState(new_state)]
            if trigger in ('distance', 'track'):
                new_state.radius, = parseargs('[float]', args[2:])
                if new_state.radius is None:
                    new_state.radius = 3.0
                if new_state.radius < 0.0:
                    message = S_NOT_POSITIVE.format(parameter = 'radius')
                    raise ValueError(message)
                if new_state.radius > MAX_DISTANCE:
                    message = S_MAXIMUM.format(parameter = 'radius',
                        value = MAX_DISTANCE)
                    raise ValueError(message)
            elif trigger == 'height':
                new_state.height, = parseargs('int', args[2:])
                if new_state.height < 0:
                    message = S_NOT_POSITIVE.format(parameter = 'height')
                    raise ValueError(message)
                new_states.append(SelectPlatformState(new_state))
        else:
            usage = TRIGGER_COMMAND_USAGES.get(command, usage)
            new_state = TriggerCommandState(command)
            new_states = [new_state, SelectButtonState(new_state)]
            if command == 'del':
                new_state.number, = parseargs('str', args[1:])
                if new_state.number != 'all':
                    new_state.number, = parseargs('int', args[1:])
            elif command == 'logic':
                new_state.logic, = parseargs('str', args[1:])
                if new_state.logic not in ('and', 'or'):
                    return usage

        player.states.exit()
        for state in new_states[:-1]:
            player.states.push(state)
        player.states.enter(new_states[-1])
    except ValueError as err:
        player.send_chat(usage)
        return str(err)
    except IndexError:
        return usage