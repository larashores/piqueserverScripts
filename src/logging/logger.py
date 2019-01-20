"""
Logs when players are on and off the server. Can find what players were on the server during a specific time interval by
using /findusers timeinterval1 timeinterval2. Each time interval should be in the form hour:minute[:day][:month][:year],
where the day, month, and year are all optional. They default to the current, date. Logs are saved to logs\log.db
"""

from piqueserver.commands import command
from logging.sqlitecommands import *
from logging.loggerconnection import logger_connection
from logging.loggerprotocol import logger_protocol
from logging.timeutil import current_timestamp, time_string, parse_time_string


STRING_LOGGED_ON_MESSAGE = '{}({}) was logged on from {} to {}\n'


@command('findusers', admin_only=True)
def find_users(connection, time1, time2):
    from_time = parse_time_string(time1)
    to_time = parse_time_string(time2)
    if from_time > current_timestamp():
        return "Time range hasn't happened yet"
    cur = connection.protocol.cursor
    cur.execute(COMMAND_SELECT_CONNECTION_EVENTS, [to_time])
    before_end_connections = set(col[0] for col in cur.fetchall())
    cur.execute(COMMAND_SELECT_DISCONNECTION_EVENTS, [from_time])
    before_beginning_disconnections = set(col[0] for col in cur.fetchall())
    logged_in_ids = before_end_connections - before_beginning_disconnections
    message = ''
    for id_ in logged_in_ids:
        cur.execute(COMMAND_SELECT_CONNECTION, [id_])
        name, ip = cur.fetchone()
        cur.execute(COMMAND_SELECT_CONNECTION_TIME, [id_])
        connection_time = time_string(cur.fetchone())
        cur.execute(COMMAND_SELECT_DISCONNECTION_TIME, [id_])
        disconnecion_time = time_string(cur.fetchone())
        message += STRING_LOGGED_ON_MESSAGE.format(name, ip, connection_time, disconnecion_time)
    if len(logged_in_ids) == 0:
        message = 'No users were logged in'
    return message


def apply_script(protocol, connection, config):
    return logger_protocol(protocol), logger_connection(connection)
