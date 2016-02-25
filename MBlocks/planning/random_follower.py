from MBlocks.planning.planner import Planner

from collections import defaultdict
from multiprocessing.dummy import Pool as ThreadPool

class RandomLightPlanner(Planner):
    def __init__(self, bots, thresh=100, ratio=0.5,
                     traverse='traverse'):
        super(RandomLightPlanner, self).__init__(bots)

        self.thresh = thresh
        self.ratio = ratio

        self._traverse = traverse
        self.state = defaultdict(lambda: None)

    def next_moves(self):
        pool = ThreadPool()
        pool.map(self._find_move, self.bots)

        return moves

    def _find_moves(self, bot):
        lights = bot.read_light_sensors()
        center = tuple(bot.find_plane())

        ratio = max(lights['forward'], lights['reverse']) / float(max(lights.values()))

        if center == (0, 0, 1) or center == (0, 0, -1):
            return self._random_jump(bot)
        elif ratio < self.ratio:
            # if forward and reverse are almost the same, do random move
            return self._random_jump(bot)
        elif lights['forward'] > lights['reverse']:
            return [bot.do_action, self._traverse, 'forward']
        else:
            return [bot.do_action, self._traverse, 'forward']
    
    def _random_jump(self, bot):
        center = tuple(bot.find_plane())
        if center == (0, 0, 1) or center == (0, 0, -1):
            return [bot.ser.write, 'bldcaccel f 6000 700\n']
        else:
            return [bot.ser.write, 'cp b f 5000 50\n']
