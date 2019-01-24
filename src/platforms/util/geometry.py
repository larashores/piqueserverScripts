from itertools import product


def aabb_colision(x, y, z, x1, y1, z1, x2, y2, z2):
    return (x1 <= x < x2) and (y1 <= y < y2) and (z1 <= z < z2)


def prism(x1, y1, z1, x2, y2, z2):
    return product(range(x1, x2), range(y1, y2), range(z1, z2))


def plane_least_rows(x1, y1, x2, y2, z):
    if y2 - y1 < x2 - x1:
        for y in range(y1, y2):
            yield x1, y, z, x2 - 1, y, z
    else:
        for x in range(x1, x2):
            yield x, y1, z, x, y2 - 1, z
