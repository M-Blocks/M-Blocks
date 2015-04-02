import networkx as nx

class Configuration:
    dx = [1, -1, 0, 0, 0, 0]
    dy = [0, 0, 1, -1, 0, 0]
    dz = [0, 0, 0, 0, 1, -1]

    def __init__(self, cubes):
        if cubes and len(cubes[0]) != 3:
            raise IndexError

        self._cubes = cubes
        # Build the underlying graph
        self._graph = nx.Graph()
        self._graph.add_nodes_from(self._cubes)
        print self._graph

    def _boundary(self):
        # doesn't matter which extreme
        extreme = self._extreme(min, min, min)
        starting_position = self._empty_neighbors(extreme)[0]

        boundary = set()
        marcher = self._rotate(starting_position, (0, 0, -1))
        while marcher != starting_position:
            boundary.update(self._neighbors(marcher))

        return boundary

    def _mobile(self):
        pass

    def _non_splitting(self):
        pass

    def _extreme(self, f, g, h):
        # f, g, h are min/max functions
        x = f(cube[0] for cube in self._cubes)
        y = g(cube[1] for cube in self._cubes)
        z = h(cube[2] for cube in self._cubes)

        return (x, y, z)

    def _is_connected(self):
        return self._graph.is_connected()

    def _neighbors(self, cube):
        if cube in self._graph.nodes():
            return self._graph.all_neighbors(cube)

        result = []
        for position in zip(dx, dy, dz):
            if position in self._graph.nodes():
                result.append(position)
        return result

    def _empty_neighbors(self, cube):
        neighbors = self._neighbors(cube)
        result = []
        for position in zip(dx, dy, dz):
            if position not in neighbors:
                 result.append(position)
        return result

    def flatten(self):
        pass
