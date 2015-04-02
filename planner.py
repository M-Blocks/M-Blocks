import re
import sys

sys.path.insert(0, '/home/sebii/Documents/Study/MIT/PhD/Code/Reconfiguration')

from controller import Cube
from Configuration import Configuration

class Planner:
    def __init__(self, cubes, positions):
        self._positions = positions
        self._cubes = cubes
        self._cube_at_pos = dict(zip(positions, cubes))

    def flatten(self):
        # easiest to save to a file and read from it
        config = Configuration(self._positions, False, False, True, 'tmp')
        config.flatten()

        moves = []
        with open('tmp_steps.record', 'r') as f:
            lines = f.readlines()
            for line in lines:
                move = self._line_parser(line)
                if move is not None:
                    cube = self._cube_at_pos[move[0]]
                    self._cube_at_pos[move[1]] = cube

                    moves.append((move, cube))

        self.moves = moves

    def solve(self):
        for move, cube in self.moves:
            dx, dy, dz = (move[1][i] - move[0][i] for i in range(3))
            print move, cube

    def _line_parser(self, line):
        elems = line.split(';')
        if len(elems) <= 2:
            return None

        result = []
        for elem in elems[:2]:
            nums = [int(x) for x in re.findall('\d+', elem)]
            result.append((nums[0], nums[1], nums[2]))

        return result

if __name__ == '__main__':
    planner = Planner(['cube_1', 'cube_2', 'cube_3', 'cube_4',
                       'cube_5', 'cube_6', 'cube_7', 'cube_8'],
                      [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0),
                       (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 1)])
    planner.flatten()
    planner.solve()
