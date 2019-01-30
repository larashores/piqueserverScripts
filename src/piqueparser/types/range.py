from piqueparser.piqueargsexception import StopParsingException


def range_class(numeric_type):
    class Range:
        def __init__(self, min=None, max=None, clamp=False, name='parameter'):
            self._min = numeric_type(min) if min else None
            self._max = numeric_type(max) if max else None
            self._clamp = clamp
            self._name = name

        def __call__(self, value=None):
            if value is None:
                return numeric_type()
            value = numeric_type(value)
            return Range.check_value(self._name, value, self._min, self._max, self._clamp)

        @staticmethod
        def check_value(name, value, min=None, max=None, clamp=None):
            if clamp:
                if min is not None and value < min:
                    return min
                if max is not None and value > max:
                    return max
            if (min is not None and value < min) or (max is not None and value > max):
                if min is None:
                    raise StopParsingException("ERROR: Maximum value of '{}' is {}".format(name, max))
                elif max is None:
                    raise StopParsingException("ERROR: Minimum value of '{}' is {}".format(name, min))
                else:
                    raise StopParsingException("ERROR: '{}' must be in the range [{}..{}]".format(name, min, max))
            return value
    return Range


IntRange = range_class(int)
FloatRange = range_class(float)
