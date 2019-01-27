from playerstates.buildingstate import BuildingState


class PlatformState(BuildingState):
    def on_inspect_platform(self, platform):
        self.player.send_chat("Platform '{}', height {}".format(platform.label, platform.height))
        return True
