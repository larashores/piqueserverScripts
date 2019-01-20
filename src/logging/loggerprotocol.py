import os
import sqlite3
from logging.sqlitecommands import COMMANDS_CREATE_TABLES

PATH = r'logs\log.db'


def logger_protocol(protocol):
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
