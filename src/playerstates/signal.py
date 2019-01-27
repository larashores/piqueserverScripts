class Signal:
    def __init__(self):
        self._connections = []

    def __call__(self, *args, **kwargs):
        for func in self._connections:
            func(*args, **kwargs)

    def connect(self, func):
        if func not in self._connections:
            self._connections.append(func)

    def disconnect(self, func):
        if func in self._connections:
            self._connections.remove(func)

    def clear(self):
        self._connections.clear()
