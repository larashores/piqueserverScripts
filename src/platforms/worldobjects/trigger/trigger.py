from playerstates.signal import Signal
from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta


class Trigger(metaclass=ABCMeta):
    NAME = abstractattribute
    ONE_PER_BUTTON = False

    def __init__(self, protocol, negate):
        self.signal_fire = Signal()
        self.signal_remove = Signal()
        self._protocol = protocol
        self._negate = negate

    def update(self, *args, **kwargs):
        pass

    def destroy(self):
        self.signal_remove(self)
        self.signal_fire.clear()
        self.signal_remove.clear()

    def status(self):
        return self._status() ^ self._negate

    def serialize(self):
        return {'type': self.NAME, 'negate': self._negate}

    @staticmethod
    def unserialize(protocol, button, data):
        from platforms.worldobjects.trigger.distancetrigger import DistanceTrigger
        from platforms.worldobjects.trigger.heighttrigger import HeightTrigger
        from platforms.worldobjects.trigger.presstrigger import PressTrigger
        from platforms.worldobjects.trigger.timertrigger import TimerTrigger

        trigger_classes = {cls.NAME: cls for cls in (DistanceTrigger, HeightTrigger, PressTrigger, TimerTrigger)}
        trigger_classes['track'] = DistanceTrigger
        cls = trigger_classes[data.pop('type')]
        return cls._unserialize(protocol, button, data)

    @staticmethod
    def _unserialize(protocol, button, data):
        pass

    @abstractmethod
    def _status(self):
        return False

    def _fire_if_active(self):
        if self.status():
            self.signal_fire()
