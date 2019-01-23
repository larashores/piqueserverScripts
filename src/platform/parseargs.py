import builtins

S_TOO_MANY_PARAMETERS = 'ERROR: too many parameters'
S_NOT_ENOUGH_PARAMETERS = 'ERROR: not enough parameters'
S_WRONG_PARAMETER_TYPE = 'ERROR: wrong parameter type'


def parseargs(signature, args):
    signature = signature.split()
    if len(args) > len(signature):
        raise ValueError(S_TOO_MANY_PARAMETERS)
    result = []
    optional = False
    for i, s in enumerate(signature):
        func_name = s.strip('[]')
        optional = optional or func_name != s
        try:
            typecast = getattr(builtins, func_name)
            result.append(typecast(args[i]))
        except ValueError:
            raise ValueError(S_WRONG_PARAMETER_TYPE)
        except IndexError:
            if not optional:
                raise ValueError(S_NOT_ENOUGH_PARAMETERS)
            result.append(None)
    return result
