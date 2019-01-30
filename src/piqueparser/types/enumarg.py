from piqueparser.piqueargsexception import PiqueArgsException


class EnumArg:
    def __init__(self, enum_type):
        self._enum_type = enum_type

    def __call__(self, value):
        return self.check_value(self._enum_type, value)

    @staticmethod
    def check_value(enum_type, value):
        try:
            return enum_type(value.upper())
        except KeyError:
            raise PiqueArgsException('Invalid enum {}'.format(value))
