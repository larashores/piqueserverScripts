from playerstates.signal import Signal


class Trigger:
    NAME = None
    ONE_PER_BUTTON = False

    def __init__(self, protocol, negate=False):
        self.protocol = protocol
        self.negate = negate
        self.signal_fire = Signal()
        self.affected_players = set()
        self._status = False

    def unbind(self):
        pass

    def get_status(self):
        return self._status ^ self.negate

    def serialize(self):
        return {'type': self.NAME, 'negate': self.negate}
