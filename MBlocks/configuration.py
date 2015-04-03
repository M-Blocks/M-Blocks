from MBlocks import utils

import itertools
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

    def flatten(self):
        pass
