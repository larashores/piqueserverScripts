class StateStack:
    def __init__(self, player):
        self._stack = []
        self._player = player

    def top(self):
        return self._stack[-1] if self._stack else None

    def push(self, *states):
        for state in states:
            state.player = self._player
            state.signal_exit.connect(self._on_signal_exit)
            self._stack.append(state)
        result = states[-1].on_enter()
        if result:
            self._player.send_chat(result)

    def pop(self):
        old_state = self._stack.pop()
        old_state.signal_exit.disconnect(self._on_signal_exit)
        result = old_state.on_exit()
        if result:
            self._player.send_chat(result)
        new_state = self.top()
        if new_state:
            result = new_state.on_enter()
            if result:
                self._player.send_chat(result)

    def clear(self):
        while self._stack:
            self.pop()

    def _on_signal_exit(self, exiting_state):
        if exiting_state == self.top():
            self.pop()
