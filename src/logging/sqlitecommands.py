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
            damage_given INTEGER NOT NULL,
            damage_taken INTEGER NOT NULL,
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
        )''',
    ''' CREATE TABLE IF NOT EXISTS text_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER UNIQUE NOT NULL REFERENCES events(id),
            text TEXT NOT NULL
        )''',
    ''' CREATE TABLE IF NOT EXISTS chat_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_event_id INTEGER UNIQUE NOT NULL REFERENCES text_events(id),
            connection_id INTEGER NOT NULL REFERENCES connections(id),
            team INTEGER NOT NULL
        )''',
    ''' CREATE TABLE IF NOT EXISTS command_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_event_id INTEGER UNIQUE NOT NULL REFERENCES text_events(id),
            connection_id INTEGER NOT NULL REFERENCES connections(id)
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
    INSERT INTO connections (ip, name_id, kills, deaths, damage_given, damage_taken)
    values (?, ?, 0, 0, 0, 0)'''

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

COMMAND_SELECT_FROM_CONNECTION = '''\
    SELECT {}
    FROM connections
    WHERE id == ?'''

COMMAND_UPDATE_CONNECTION = '''\
    UPDATE connections
    SET {} = ?
    WHERE id == ?'''

COMMAND_INSERT_TEXT_EVENT = '''
    INSERT INTO text_events (event_id, text)
    values (?, ?)'''

COMMAND_INSERT_CHAT_EVENT = '''
    INSERT INTO chat_events (text_event_id, team, connection_id)
    values (?, ?, ?)'''

COMMAND_INSERT_COMMAND_EVENT = '''
    INSERT INTO command_events (text_event_id, connection_id)
    values (?, ?)'''

COMMAND_SELECT_KILLS = COMMAND_SELECT_FROM_CONNECTION.format('kills')
COMMAND_SELECT_DEATHS = COMMAND_SELECT_FROM_CONNECTION.format('deaths')
COMMAND_SELECT_DAMAGE_TAKEN = COMMAND_SELECT_FROM_CONNECTION.format('damage_taken')
COMMAND_SELECT_DAMAGE_GIVEN = COMMAND_SELECT_FROM_CONNECTION.format('damage_given')

COMMAND_UPDATE_KILLS = COMMAND_UPDATE_CONNECTION.format('kills')
COMMAND_UPDATE_DEATHS = COMMAND_UPDATE_CONNECTION.format('deaths')
COMMAND_UPDATE_DAMAGE_TAKEN = COMMAND_UPDATE_CONNECTION.format('damage_taken')
COMMAND_UPDATE_DAMAGE_GIVEN = COMMAND_UPDATE_CONNECTION.format('damage_given')
