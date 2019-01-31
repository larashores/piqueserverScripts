import builtins

S_TOO_MANY_PARAMETERS = 'ERROR: too many parameters'
S_NOT_ENOUGH_PARAMETERS = 'ERROR: not enough parameters'
S_WRONG_PARAMETER_TYPE = 'ERROR: wrong parameter type'


def invalid_range(x, y, z):
    return (x < 0) or (x > 512) or (y < 0 or y > 512) or (z < 0) or (z > 64)


def sign(x):
    return (x > 0) - (x < 0)


def parseargs(signature, args):
    signature = signature.split()
    if len(args) > len(signature):
        raise ValueError(S_TOO_MANY_PARAMETERS)
    result = []
    optional = False
    for i, type_desc in enumerate(signature):
        type_name = type_desc.strip('[]')
        optional = optional or type_name != type_desc
        try:
            typecast = getattr(builtins, type_name)
            result.append(typecast(args[i]))
        except ValueError:
            raise ValueError(S_WRONG_PARAMETER_TYPE)
        except IndexError:
            if not optional:
                raise ValueError(S_NOT_ENOUGH_PARAMETERS)
            result.append(None)
    return result
