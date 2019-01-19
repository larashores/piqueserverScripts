"""
Logs when players are on and off the server. Can find what players were on the server during a specific time interval by
using /findusers timeinterval1 timeinterval2 day month year. Each time interval should be in the form hour:minute:second
If the intervals are the same it finds the users logged on at that point in time. If day, month, or year is left out it
will use the current day, month, or year at the time the command is used. Logs are saved to logs\playerlog.db
"""

import sqlite3
import os
import time
from datetime import datetime, timezone

from piqueserver.commands import command

PATH = r'logs\playerlog.db'

COMMANDS_CREATE_TABLES = [
    ''' CREATE TABLE IF NOT EXISTS display_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )''',
    ''' CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            kills INTEGER NOT NULL,
            deaths INTEGER NOT NULL,
            name_id INTEGER NOT NULL REFERENCES display_names(id)
        )''',
    ''' CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time INTEGER NOT NULL
        )''',
    ''' CREATE TABLE IF NOT EXISTS connection_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER UNIQUE NOT NULL REFERENCES events(id),
            connection_id INTEGER UNIQUE NOT NULL REFERENCES connections(id)
        )''',
    ''' CREATE TABLE IF NOT EXISTS disconnection_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER UNIQUE NOT NULL REFERENCES events(id),
            connection_id INTEGER UNIQUE NOT NULL REFERENCES connections(id)
        )'''
]

COMMAND_SELECT_NAME = '''\
    SELECT id
    FROM display_names
    WHERE name == ?'''

COMMAND_INSERT_NAME = '''\
    INSERT INTO display_names (name)
    VALUES (?)'''

COMMAND_INSERT_CONNECTION = '''\
    INSERT INTO connections (ip, name_id, kills, deaths)
    values (?, ?, 0, 0)'''

COMMAND_INSERT_EVENT = '''\
    INSERT INTO events (time)
    VALUES (?)'''

COMMAND_INSERT_CONNECTION_EVENT = '''
    INSERT INTO connection_events (event_id, connection_id)
    values (?, ?)'''

COMMAND_INSERT_DISCONNECTION_EVENT = '''
    INSERT INTO disconnection_events (event_id, connection_id)
    values (?, ?)'''

COMMAND_SELECT_CONNECTION_EVENTS = '''\
    SELECT connection_id
    FROM events INNER JOIN connection_events 
        ON connection_events.event_id == events.id
    WHERE time <= ?'''

COMMAND_SELECT_DISCONNECTION_EVENTS = '''\
    SELECT connection_id
    FROM events INNER JOIN disconnection_events 
        ON disconnection_events.event_id == events.id
    WHERE time <= ?'''

COMMAND_SELECT_CONNECTION = '''\
    SELECT name, ip
    FROM connections INNER JOIN display_names
        ON connections.name_id == display_names.id
    WHERE connections.id == ?'''

COMMAND_SELECT_CONNECTION_TIME = '''\
    SELECT time
    FROM events INNER JOIN connection_events 
        ON connection_events.event_id == events.id
    WHERE connection_id == ?'''

COMMAND_SELECT_DISCONNECTION_TIME = '''\
    SELECT time
    FROM events INNER JOIN disconnection_events 
        ON disconnection_events.event_id == events.id
    WHERE connection_id == ?'''

COMMAND_SELECT_KILLS = '''\
    SELECT kills
    FROM connections
    WHERE id == ?'''

COMMAND_SELECT_DEATHS = '''\
    SELECT deaths
    FROM connections
    WHERE id == ?'''

COMMAND_UPDATE_KILLS = '''\
    UPDATE connections
    SET kills = ?
    WHERE id == ?'''

COMMAND_UPDATE_DEATHS = '''\
    UPDATE connections
    SET kills = ?
    WHERE id == ?'''

STRING_LOGGED_ON_MESSAGE = '{}({}) was logged on from {} to {}\n'


def get_seconds(time_string):
    hours, minutes = time_string.split(':')
    return int(hours)*3600 + int(minutes)*60


def get_from_to_seconds(time1, time2, day, month, year):
    current_time = time.localtime()
    if day is None:
        day = current_time.tm_mday
    if month is None:
        month = current_time.tm_mon
    if year is None:
        year = current_time.tm_year
    timestamp = time.mktime(time.gmtime(datetime(int(year), int(month), int(day)).timestamp()))
    return timestamp + get_seconds(time1), timestamp + get_seconds(time2)


def current_timestamp():
    return datetime.utcnow().timestamp()


def time_string(timestamp):
    if timestamp is None:
        return 'now'
    dtime = datetime.fromtimestamp(int(timestamp[0])).replace(tzinfo=timezone.utc).astimezone()
    return dtime.strftime('%H:%M')


@command('findusers', admin_only=True)
def find_users(connection, time1, time2, day=None, month=None, year=None):
    from_time, to_time = get_from_to_seconds(time1, time2, day, month, year)
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

        def on_kill(self, killer, *args):
            cur = self.protocol.cursor
            cur.execute(COMMAND_SELECT_DEATHS, self.connection_id)
            deaths = cur.fetchone()[0]
            cur.execute(COMMAND_UPDATE_DEATHS, deaths + 1, self.connection_id)
            if killer is not None:
                cur.execute(COMMAND_SELECT_KILLS, killer.connection_id)
                kills = cur.fetchone()[0]
                cur.execute(COMMAND_UPDATE_KILLS, kills + 1, killer.connection_id)
            self.protocol.log_connection.commit()
            return connection.on_kill(self, killer, *args)

    return LoggerProtocol, LoggerConnection
