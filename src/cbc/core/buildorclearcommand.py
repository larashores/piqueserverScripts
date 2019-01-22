from abc import abstractmethod, ABCMeta
from cbc.core import state


class BuildOrRemoveState(state.BuildingState, metaclass=ABCMeta):
    def __init__(self, player, build=True):
        state.BuildingState.__init__(self, player)
        if build:
            self.on_block_build = self.on_block
        else:
            self.on_block_removed = self.on_block

    @abstractmethod
    def on_block(self, x, y, z):
        pass
