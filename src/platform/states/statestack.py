class StateStack:
    stack = None
    protocol = None
    connection = None

    def __init__(self, connection):
        self.stack = []
        self.connection = connection
        self.protocol = connection.protocol

    def top(self):
        return self.stack[-1] if self.stack else None

    def enter(self, state):
        self.stack.append(state)
        result = state.on_enter(self.protocol, self.connection)
        if result:
            self.connection.send_chat(result)

    def push(self, state):
        self.stack.append(state)

    def pop(self):
        state = self.stack.pop()
        result = state.on_exit(self.protocol, self.connection)
        if result:
            self.connection.send_chat(result)
        state = self.top()
        if state:
            result = state.on_enter(self.protocol, self.connection)
            if result:
                self.connection.send_chat(result)

    def exit(self):
        while self.stack:
            self.pop()
