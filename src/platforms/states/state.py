class State(object):
    name = None
    blocking = False
    parent_state = None

    def on_enter(self, protocol, player):
        pass

    def on_exit(self, protocol, player):
        pass

    def get_parent(self):
        return self.parent_state if self.parent_state else self
