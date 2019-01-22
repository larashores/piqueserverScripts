from abc import abstractmethod, ABCMeta
from cbc.core import buildingstate


class BuildOrRemoveState(buildingstate.BuildingState, metaclass=ABCMeta):
    BUILD_STATE = True

    def __init__(self, *args, **kwargs):
        buildingstate.BuildingState.__init__(self, *args, **kwargs)
        if self.BUILD_STATE:
            self.on_block_build = self.on_block
        else:
            self.on_block_removed = self.on_block

    @abstractmethod
    def on_block(self, x, y, z):
        pass
