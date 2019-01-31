import itertools


def aabb_collision(x, y, z, x1, y1, z1, x2, y2, z2):
    return (x1 <= x <= x2) and (y1 <= y <= y2) and (z1 <= z <= z2)


def prism_range(x1, y1, z1, x2, y2, z2):
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    z1, z2 = min(z1, z2), max(z1, z2)
    return itertools.product(range(x1, x2), range(y1, y2), range(z1, z2))
