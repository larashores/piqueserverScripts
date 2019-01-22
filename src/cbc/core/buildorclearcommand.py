from abc import abstractmethod, ABCMeta


def build_or_clear_connection(connection, build=True):
    class BuildOrClearConnection(connection, metaclass=ABCMeta):
        def __init__(self, *arg, **kwargs):
            connection.__init__(self, *arg, **kwargs)
            if build:
                def on_block_build(self, x, y, z):
                    self.on_block(x, y, z)
                    return connection.on_block_build(self, x, y, z)
                self.on_block_build = on_block_build
            else:
                def on_block_removed(self, x, y, z):
                    self.on_block(x, y, z)
                    return connection.on_block_removed(self, x, y, z)
                self.on_block_removed = on_block_removed

        @abstractmethod
        def on_block(self, point1, point2):
            pass

    return BuildOrClearConnection
