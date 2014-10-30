import math
import numpy

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
    rot = numpy.array([[numpy.cos(theta), numpy.sin(theta)],
                       [-numpy.sin(theta), numpy.cos(theta)]])
    vec = numpy.array(v)
    res = dot(rot, vec)
    res[res < 1e-8] = 0

    return res.tolist()
