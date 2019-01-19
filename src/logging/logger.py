"""
Logs when players are on and off the server. Can find what players were on the server during a specific time interval by
using /findusers timeinterval1 timeinterval2 day month year. Each time interval should be in the form hour:minute:second
If the intervals are the same it finds the users logged on at that point in time. If day, month, or year is left out it
will use the current day, month, or year at the time the command is used. Logs are saved to logs\playerlog.db
"""

import sqlite3
import os
import time
import enum
from datetime import datetime, timezone

from piqueserver.commands import command
from logging.sqlitecommands import *

PATH = r'logs\log.db'

STRING_LOGGED_ON_MESSAGE = '{}({}) was logged on from {} to {}\n'


class MessageType(enum.Enum):
    BLUE = 0
    GREEN = 1
    GLOBAL = 2
    UNKNOWN = 3


def get_seconds(time_string):
    """
    Returns the seconds past epoch when given a time string in local time
    Should be in any of the following formats:
        HH::MM, HH:MM::dd, HH::MM::dd::mm, HH::MM::dd::mm::yyyy
    """
    current_time = time.localtime()
    values = time_string.split(':')
    if not 2 <= len(values) <= 5:
        raise ValueError('Incorrect time_string format')
    elif len(values) == 2:
        hours, minutes = values
        day = current_time.tm_mday
        month = current_time.tm_mon
        year = current_time.tm_year
    elif len(values) == 3:
        hours, minutes, day = values
        month = current_time.tm_mon
        year = current_time.tm_year
    elif len(values) == 4:
        hours, minutes, day, month = values
        year = current_time.tm_year
    elif len(values) == 5:
        hours, minutes, day, month, year = values

    d_time = datetime(int(year), int(month), int(day), int(hours), int(minutes))
    return time.mktime(time.gmtime(d_time.timestamp()))


def current_timestamp():
    return datetime.utcnow().timestamp()


def time_string(timestamp):
    if timestamp is None:
        return 'now'
    dtime = datetime.fromtimestamp(int(timestamp[0])).replace(tzinfo=timezone.utc).astimezone()
    return dtime.strftime('%H:%M')


@command('findusers', admin_only=True)
def find_users(connection, time1, time2):
    from_time = get_seconds(time1)
    to_time = get_seconds(time2)
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
    class LoggerProtocol(protocol):
        def __init__(self, *args, **kwargs):
            protocol.__init__(self, *args, **kwargs)
            path = os.path.join(os.getcwd(), PATH)
            top = os.path.dirname(path)
            if not os.path.exists(top):
                os.makedirs(top)
            self.log_connection = sqlite3.connect(os.path.join(os.getcwd(), PATH))
            self.cursor = self.log_connection.cursor()
            for command in COMMANDS_CREATE_TABLES:
                self.cursor.execute(command)
            self.log_connection.commit()

    class LoggerConnection(connection):
        def __init__(self, *args, **kwargs):
            connection.__init__(self, *args, **kwargs)
            self.connection_id = None

        def on_login(self, name):
            cur = self.protocol.cursor
            cur.execute(COMMAND_SELECT_NAME, [name])
            result = cur.fetchone()
            if result is None:
                cur.execute(COMMAND_INSERT_NAME, [name])
                name_id = cur.lastrowid
            else:
                name_id = result[0]
            cur.execute(COMMAND_INSERT_CONNECTION, [self.address[0], name_id])
            self.connection_id = cur.lastrowid
            cur.execute(COMMAND_INSERT_EVENT, [current_timestamp()])
            event_id = cur.lastrowid
            cur.execute(COMMAND_INSERT_CONNECTION_EVENT, [event_id, self.connection_id])
            self.protocol.log_connection.commit()
            return connection.on_login(self, name)

        def on_disconnect(self):
            cur = self.protocol.cursor
            cur.execute(COMMAND_INSERT_EVENT, [current_timestamp()])
            event_id = cur.lastrowid
            cur.execute(COMMAND_INSERT_DISCONNECTION_EVENT, [event_id, self.connection_id])
            self.protocol.log_connection.commit()
            return connection.on_disconnect(self)

        def on_kill(self, killer, *args, **kwargs):
            cur = self.protocol.cursor
            cur.execute(COMMAND_SELECT_DEATHS, self.connection_id)
            deaths = cur.fetchone()[0]
            cur.execute(COMMAND_UPDATE_DEATHS, deaths + 1, self.connection_id)
            if killer is not None:
                cur.execute(COMMAND_SELECT_KILLS, killer.connection_id)
                kills = cur.fetchone()[0]
                cur.execute(COMMAND_UPDATE_KILLS, kills + 1, killer.connection_id)
            self.protocol.log_connection.commit()
            return connection.on_kill(self, killer, *args, **kwargs)

        def set_hp(self, hp, player=None, **kwargs):
            if hp <= self.hp:
                hp = max(0, hp)
                hit_amount = self.hp - hp
                cur = self.protocol.cursor
                cur.execute(COMMAND_SELECT_DAMAGE_TAKEN, [self.connection_id])
                damage_taken = cur.fetchone()[0]
                cur.execute(COMMAND_UPDATE_DAMAGE_TAKEN, [damage_taken + hit_amount, self.connection_id])
                if player is not None:
                    cur.execute(COMMAND_SELECT_DAMAGE_GIVEN, [player.connection_id])
                    damage_given = cur.fetchone()[0]
                    cur.execute(COMMAND_UPDATE_DAMAGE_GIVEN, [damage_given + hit_amount, player.connection_id])
                self.protocol.log_connection.commit()
            return connection.set_hp(self, hp, player, **kwargs)

        def on_chat_sent(self, value, global_message):
            if global_message:
                msg_type = MessageType.GLOBAL
            elif self.team.id == 0:
                msg_type = MessageType.BLUE
            elif self.team.id == 1:
                msg_type = MessageType.GREEN
            else:
                msg_type = MessageType.UNKNOWN
            cur = self.protocol.cursor
            cur.execute(COMMAND_INSERT_EVENT, [current_timestamp()])
            event_id = cur.lastrowid
            cur.execute(COMMAND_INSERT_TEXT_EVENT, [event_id, value])
            text_event_id = cur.lastrowid
            cur.execute(COMMAND_INSERT_CHAT_EVENT, [text_event_id, msg_type.value, self.connection_id])
            self.protocol.log_connection.commit()
            return connection.on_chat_sent(self, value, global_message)

        def on_command(self, command, parameters):
            text = chr(92) + command + ' ' + ' '.join(parameters)
            cur = self.protocol.cursor
            cur.execute(COMMAND_INSERT_EVENT, [current_timestamp()])
            event_id = cur.lastrowid
            cur.execute(COMMAND_INSERT_TEXT_EVENT, [event_id, text])
            text_event_id = cur.lastrowid
            cur.execute(COMMAND_INSERT_COMMAND_EVENT, [text_event_id, self.connection_id])
            self.protocol.log_connection.commit()
            return connection.on_command(self, command, parameters)

    return LoggerProtocol, LoggerConnection
