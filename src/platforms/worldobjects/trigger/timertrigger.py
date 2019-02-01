from platforms.worldobjects.trigger.trigger import Trigger


from twisted.internet.task import LoopingCall


class TimerTrigger(Trigger):
    NAME = 'timer'

    def __init__(self, protocol, negate, interval, amount):
        Trigger.__init__(self, protocol, negate)
        self._firing = False
        self._timer_loop = LoopingCall(self._on_timer)
        self._amount_left = amount
        self._interval = interval
        self._timer_loop.start(interval)

    def _on_timer(self):
        if self._amount_left == 0:
            self._timer_loop.stop()
        self._firing = True
        self.signal_fire()
        self._firing = False
        if self._amount_left > 0:
            self._amount_left -= 1

    def destroy(self):
        self._timer_loop.stop()
        Trigger.destroy(self)

    def _status(self):
        return self._firing

    def serialize(self):
        return {
            **Trigger.serialize(self),
            'interval': self._interval,
            'amount_left': self._amount_left
        }

    @staticmethod
    def _unserialize(protocol, button, data):
        platform = protocol.get_platform(data['platform_id'])
        return TimerTrigger(protocol, data['negate'], data['interval'], data['amount'])

    def __str__(self):
        return "{}timer:{}s".format(
            'NOT ' if self._negate else '', self._interval)
