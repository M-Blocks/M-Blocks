from MBlocks.controller import *
from MBlocks.utils import *


def light_follower(cube):
	sensors = cube._read_light_sensors()
	avg_value = sum(sensors.values()) / float(len(sensors.values()))
	sensors = {k : v if v > avg_value}

	dirs = [(1, 0, 0), (-1, 0, 0),
            (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1)]

    
	print sensors


def positions(cubes):
	return [cube.position for cube in cubes]


def rotate(self, cube, direction):
    """Rotate cube in a given direction.

    Does nothing if the move cannot be performed.
    """
    axis = 0
    posneg = direction[axis]
    while posneg == 0:
        axis = axis + 1
        posneg = direction[axis]
        
    c1_c3_wrapped_coords = [((0,0,+posneg),(0,+1,0)),
                            ((0,+1,0),(0,0,-posneg)),
                            ((0,0,-posneg),(0,-1,0)),
                            ((0,-1,0),(0,0,+posneg))]
    
    for (i, j) in c1_c3_wrapped_coords:
        #    c6 c7
        # c4 c3 c2
        # c5 cube c1
        # c9 c8
        i = utils.circshift(i, -axis)
        j = utils.circshift(j, -axis)
        c1 = utils.add(i, cube)
        c3 = utils.add(j, cube)
        c2 = utils.add(utils.add(i, j), cube)                  #(c1[0]+c3[0], c1[1]+c3[1])
        c6 = utils.add(utils.mult(j, 2), cube)                 #(2*c3[0], 2*c3[1])
        c7 = utils.add(utils.add(i, utils.mult(j, 2)), cube)   #(c1[0]+2*c3[0], c1[1]+2*c3[1])
        c5 = utils.add(utils.mult(i, -1), cube)                #(-c1[0], -c1[1])
        c4 = utils.add(utils.add(j, utils.mult(i, -1)), cube)  #(c3[0]-c1[0], c3[1]-c1[1])
        c8 = utils.add(utils.mult(j, -1), cube)
        c9 = utils.add(utils.add(utils.mult(i, -1), utils.mult(j, -1)), cube)

        cube_positions = positions(cubes)
        if not c1 in cube_positions:
            continue
        if c3 in cube_positions:
            continue
        if c5 in cube_positions:
            continue

        # Transfer Move
        if c4 in cube_positions:
            return c5
        # Linear Move
        elif c2 in cube_positions:
            return c3
        # Transfer Move
        elif c6 in cube_positions or c7 in cube_positions :
            return c3
        # Corner Move
        else:
            return c2
    return cube
