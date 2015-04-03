import collections
import math
import numpy as np
import sys

def sgn(x):
    """Return the sign of x.
    """
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

def add(v1, v2):
    """Add two vectors together: v1 + v2
    """
    return tuple(a + b for a, b in zip(v1, v2))

def sub(v1, v2):
    """Subtract two vectors: v1 - v2
    """
    return tuple(a - b for a, b in zip(v1, v2))

def mult(v, a):
    """Multiply a vector by a scalar: a * v
    """
    return tuple(a * x for x in v)

def circshift(v, i):
    """Circular shift of vector
    """
    return tuple(v[(i + j) % len(v)] for j in range(len(v)))

def dot(v1, v2):
    """Return the dot product between two vectors.
    """
    return sum(x * y for x, y in zip(v1, v2))

def length(v):
    """Return the length of a vector under the Euclidean norm.
    """
    return math.sqrt(dot(v, v))

def angle(v1, v2):
    """Return the angle between two vectors.
    """
    l1, l2 = length(v1), length(v2)
    v1 = [x / l1 for x in v1]
    v2 = [x / l2 for x in v2]

    d = dot(v1, v2)
    return math.acos(d)

def rotate(v, theta):
    """Rotate vector v by theta degrees.
    """
    rot = np.array([[np.cos(theta), np.sin(theta)],
                    [-np.sin(theta), np.cos(theta)]])
    vec = np.array(v)
    res = dot(rot, vec)
    res[np.absolute(res) < 1e-8] = 0

    return res.tolist()