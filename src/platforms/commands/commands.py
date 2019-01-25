from platforms.core.platformconnection import ACTION_RAY_LENGTH, ACTION_RAY_LENGTH_LONG


from platforms import piqueargs

S_SAVED = 'Platforms saved'
S_REACH = 'You can now reach to buttons from from far away'
S_NO_REACH = 'Button reach reverted to normal'


@piqueargs.command(usage=r'Usage: \save')
def save(connection):
    connection.protocol.dump_platform_json()
    return S_SAVED


@piqueargs.command(r'Usage: \reach')
def reach(connection):
    if connection not in connection.protocol.players:
        raise ValueError()
    long = connection.reach == ACTION_RAY_LENGTH_LONG
    connection.reach = ACTION_RAY_LENGTH if long else ACTION_RAY_LENGTH_LONG
    return S_REACH if not long else S_NO_REACH
