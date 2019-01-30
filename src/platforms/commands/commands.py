from platforms.util import piqueargs


@piqueargs.command(usage=r'Usage: \save')
def save(connection):
    connection.protocol.dump_platform_json()
    return 'Platforms saved'
