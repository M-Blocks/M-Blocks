import math

def dot(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

def length(v):
    return math.sqrt(dot(v, v))

def angle(v1, v2):
    l1, l2 = length(v1), length(v2)
    v1 = [x / l1 for x in v1]
    v2 = [x / l2 for x in v2]

    d = dot(v1, v2)
    return math.acos(d)
