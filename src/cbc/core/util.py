def invalid_range(x, y, z):
    return (x < 0) or (x >= 512) or (y < 0 or y >= 512) or (z < 0) or (z > 64)


def sign(x):
    return (x > 0) - (x < 0)
