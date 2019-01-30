class PiqueArgsException(Exception):
    def __init__(self, msg, cls=None):
        self.msg = msg
        self.cls = cls
