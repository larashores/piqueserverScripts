from logging.sqlitecommands import *
from logging.timeutil import current_timestamp
import enum


class MessageType(enum.Enum):
    BLUE = 0
    GREEN = 1
    GLOBAL = 2
    UNKNOWN = 3


def logger_connection(connection):
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
