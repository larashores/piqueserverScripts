from piqueparser import piqueargs


def base_command(connection, end, state_type, usage_message):
    if not end:
        return
    if connection not in connection.protocol.players:
        raise ValueError()
    if isinstance(connection.state_stack.top(), state_type):
        connection.state_stack.clear()  # cancel command
        return
    return usage_message


def id_or_all(value=None):
    if value is None:
        return 'all'
    if value == 'all':
        return value
    try:
        return int(value)
    except ValueError:
        piqueargs.stop_parsing("Value '{}' must be 'all' or int".format(value))
