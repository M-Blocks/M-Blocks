from MBlocks import utils

import itertools
import random
from collections import deque
from operator import mul

import networkx as nx

class Config:
    dx = [1, -1, 0, 0, 0, 0]
    dy = [0, 0, 1, -1, 0, 0]
    dz = [0, 0, 0, 0, 1, -1]

    def __init__(self, cubes):
        if cubes and len(cubes[0]) != 3:
            raise IndexError

        # Build the underlying graph
        self._graph = nx.Graph()
        self._graph.add_nodes_from(cubes)
        for cube in cubes:
            for to_add in zip(Config.dx, Config.dy, Config.dz):
                neighbor = utils.add(cube, to_add)
                if neighbor in cubes:
                    self._graph.add_edge(cube, neighbor)

    def _boundary(self):
        """Return the boundary of the configuration.
        """
        min_cube = self._extreme(min, min, min)
        max_cube = self._extreme(max, max, max)

        empty_cubes = set()
        for cube in itertools.product(range(min_cube[0], max_cube[0]),
                                      range(min_cube[1], max_cube[1]),
                                      range(min_cube[2], max_cube[2])):
            if not self._has_cube(cube):
                empty_cubes.add(cube)

        holes = set()
        for cube in empty_cubes:
            # start a BFS from the current cube
            visited = set([cube])
            queue = deque([cube])

            outer = False
            while queue:
                ccube = queue.popleft()
                for to_add in zip(Config.dx, Config.dy, Config.dz):
                    ncube = utils.add(to_add, ccube)
                    if ncube in visited:
                        continue
                    visited.add(ncube)
                    queue.append(ncube)

                if len(visited) > len(empty_cubes):
                    outer = True
                    break

            if not outer:
                holes.update(visited)
 
        boundary = set()
        for cube in self._graph.nodes():
            empty_neighbors = self._empty_neighbors(cube)
            for ncube in empty_neighbors:
                if ncube not in holes:
                    boundary.add(cube)
                    break

        return boundary

    def _mobile(self):
        """Return the mobile cubes of the configuration.

        We only care about the mobile cubes that are on the boundary.
        """
        boundary = self._boundary()

        def free_plane(neighbors):
            if len(neighbors) == 0:
                return False
            if len(neighbors) == 1:
                return True
            if len(neighbors) > 2:
                return False

            for c1, c2 in itertools.combinations(neighbors, 2):
                diff = utils.sub(c1, c2)
                if abs(diff[0]) == 2 or abs(diff[1]) == 2 or abs(diff[2]) == 2:
                    return False

            return True

        mobile = set()
        for cube in boundary:
            neighbors_xy = []
            for dx, dy in zip(Config.dx, Config.dy):
                ncube = utils.add(cube, (dx, dy, 0))
                if cube != ncube and self._has_cube(ncube):
                    neighbors_xy.append(ncube)
            
            neighbors_xz = []
            for dx, dz in zip(Config.dx, Config.dz):
                ncube = utils.add(cube, (dx, 0, dz))
                if cube != ncube and self._has_cube(ncube):
                    neighbors_xz.append(ncube)

            neighbors_yz = []
            for dy, dz in zip(Config.dy, Config.dz):
                ncube = utils.add(cube, (0, dy, dz))
                if cube != ncube and self._has_cube(ncube):
                    neighbors_yz.append(ncube)

            if free_plane(neighbors_xy) or free_plane(neighbors_xz) or free_plane(neighbors_yz):
                mobile.add(cube)

        return mobile

    def _non_splitting(self):
        """Return the mobile cubes of the configuration that do not disconnect the structure.
        """
        mobile = self._mobile()
        articulation = set(nx.articulation_points(self._graph))

        return mobile - articulation

    def _extreme(self, f, g, h):
        """Return an extreme module of the configuration.

        The functions f, g, h are min/max functions depending on which extreme is needed.
        """
        # f, g, h are min/max functions
        x = f(cube[0] for cube in self._graph.nodes())
        y = g(cube[1] for cube in self._graph.nodes())
        z = h(cube[2] for cube in self._graph.nodes())

        return (x, y, z)

    def _add_cube(self, cube, neighbors):
        self._graph.add_node(cube)
        for neighbor in neighbors:
            self._graph.add_edge(cube, neighbor)
            
    def _remove_cube(self, cube):
        self._graph.remove_node(cube)
        
    def _has_cube(self, cube):
        """Returns true if cube is in the configuration.
        """
        return cube in self._graph.nodes()

    def _is_connected(self):
        """Returns true if configuration is edge connected.
        """
        return nx.is_connected(self._graph)

    def _neighbors(self, cube):
        """Returns the cube neighbors of cube in the configuration.
        """
        if cube in self._graph.nodes():
            return self._graph.neighbors(cube)

        result = []
        for to_add in zip(Config.dx, Config.dy, Config.dz):
            new_pos = utils.add(to_add, cube)
            if new_pos in self._graph.nodes():
                result.append(new_pos)
        return result

    def _empty_neighbors(self, cube):
        """Returns the empty neighbors of cube in the configuration.
        """
        neighbors = self._neighbors(cube)
        result = []
        for to_add in zip(Config.dx, Config.dy, Config.dz):
            new_pos = utils.add(to_add, cube)
            if new_pos not in neighbors:
                result.append(new_pos)
        return result

    def _slice_graph(self, dim, f, g):
        """Returns the slice graph of the configuration.

        A slice is a subconfiguration for which one axis is fixed.

        Note: f and g are min/max functions. If f is min, g is max and
          vice-versa.
        """
        min_dim = f(cube[dim] for cube in self._graph.nodes())
        max_dim = g(cube[dim] for cube in self._graph.nodes())

        slices = []
        for i in range(min_dim, max_dim + 1):
            cubes = [cube for cube in self._graph.nodes() if cube[dim] == i]
            slices.append(Config(cubes))

        return slices

    def _move_to_tail(self, cube, tail, extend):
        """Moves cube to extend tail.
        """
        self._remove_cube(cube)

        final_position = utils.add(tail, extend)
        path, moves = self._find_path(cube, final_position)
        self._add_cube(final_position, [tail])

        return list(path), final_position

    def _find_path(self, c0, c1):
        """Find a pivoting path from c0 to c1.
        """
        dirs = [(1, 0, 0), (-1, 0, 0),
                (0, 1, 0), (0, -1, 0),
                (0, 0, 1), (0, 0, -1)]

        # Do a BFS using pivoting moves to find valid positions
        prev = {}
        seen = set([c0])
        queue = deque([c0])
        while queue:
            cube = queue.popleft()

            if cube == c1:
                break
            for direction in dirs:
                next_cube = self._rotate(cube, direction)
                if next_cube not in seen:
                    seen.add(next_cube)
                    queue.append(next_cube)
                    prev[next_cube] = (cube, direction)

        # Reconstruct path
        cube = c1
        path = [c1]
        moves = []
        while cube != c0:
            cube, move = prev[cube]
            path.append(cube)
            moves.append(move)

        return reversed(path), reversed(moves)
        
    def _rotate(self, c0, direction):
        """Rotate c0 in a given direction.

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
            # c5 c0 c1
            # c9 c8
            i = utils.circshift(i, -axis)
            j = utils.circshift(j, -axis)
            c1 = utils.add(i, c0)
            c3 = utils.add(j, c0)
            c2 = utils.add(utils.add(i, j), c0)                  #(c1[0]+c3[0], c1[1]+c3[1])
            c6 = utils.add(utils.mult(j, 2), c0)                 #(2*c3[0], 2*c3[1])
            c7 = utils.add(utils.add(i, utils.mult(j, 2)), c0)   #(c1[0]+2*c3[0], c1[1]+2*c3[1])
            c5 = utils.add(utils.mult(i, -1), c0)                #(-c1[0], -c1[1])
            c4 = utils.add(utils.add(j, utils.mult(i, -1)), c0)  #(c3[0]-c1[0], c3[1]-c1[1])
            c8 = utils.add(utils.mult(j, -1), c0)
            c9 = utils.add(utils.add(utils.mult(i, -1), utils.mult(j, -1)), c0)

            if not self._has_cube(c1):
                continue
            if self._has_cube(c3):
                continue
            if self._has_cube(c5):
                continue

            # Transfer Move
            if self._has_cube(c4):
                return c5
            # Linear Move
            elif self._has_cube(c2):
                return c3
            # Transfer Move
            elif self._has_cube(c6) or self._has_cube(c7) :
                return c3
            # Corner Move
            else:
                return c2
        return c0

    def _flatten(self, tail, extend, slices):
        moves = []
        for S in reversed(slices):
            # Find a root module
            for cube in S._graph.nodes():
                neighbor = utils.add(cube, extend)
                if neighbor in self._graph.nodes():
                    root = cube
                    break
            else:
                root = None
                    
            non_splitting = S._non_splitting() - set(tail) - set([root])
            while non_splitting:
                sorted_ns = sorted(non_splitting, key=lambda c: len(self._neighbors(c)))
                cube = sorted_ns[0]
                move, tail_cube = self._move_to_tail(cube, tail[-1], extend)

                S._remove_cube(cube)
                tail.append(tail_cube)
                moves.append(move)
                non_splitting = S._non_splitting() - set(tail) - set([root])

            if root is not None:
                move, tail_cube = self._move_to_tail(root, tail[-1], extend)
                tail.append(tail_cube)
                moves.append(move)

        return moves
        
    def flatten(self):
        """Flatten configuration into a line.

        To change where the tail is, you need to change the following:
          - definition of tail to use different min/max functions
          - definition of extend
          - the dimension argument in slices
        """
        tail = [self._extreme(min, min, min)]
        extend = (0, 0, -1)
        slices = self._slice_graph(2, min, max)

        return self._flatten(tail, extend, slices)

    def reconfigure(self, new_config):
        moves_forward = self.flatten()
        moves_reverse = list(reversed([list(reversed(l)) for l in new_config.flatten()]))

        return moves_forward, moves_reverse
