from platforms.worldobjects.trigger.trigger import Trigger


from twisted.internet.task import LoopingCall


class TimerTrigger(Trigger):
    NAME = 'timer'

    def __init__(self, protocol, negate, interval, amount):
        Trigger.__init__(self, protocol, negate)
        self._firing = False
        self._timer_loop = LoopingCall(self._on_timer)
        self._target_amount = amount
        self._amount = 0
        self._interval = interval
        self._timer_loop.start(interval)

    def _on_timer(self):
        if self._amount == self._target_amount:
            self._timer_loop.stop()
        self._firing = True
        self.signal_fire()
        self._firing = False
        if self._target_amount is not None:
            self._amount += 1

    def unbind(self):
        self._timer_loop.stop()

    def _status(self):
        return self._firing

    def serialize(self):
        return {
            'type': self.type,
            'negate': self.negate,
            'platform_id': self.platform.id,
            'height': self.target_height
        }

    def __str__(self):
        return "{}timer:{}s".format(
            'NOT ' if self._negate else '', self._interva)
