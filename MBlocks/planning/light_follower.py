import operator

from MBlocks.planning.planner import Planner

from multiprocessing.dummy import Pool as ThreadPool

class LatticeLightPlanner(Planner):
    def __init__(self, bots, thresh=100, ratio=0.7,
                     traverse='traverse', change='change_plane',
                     stop_fn=None):
        super(LatticeLightPlanner, self).__init__(bots, stop_fn)

        self._traverse = traverse
        self._change = change
        
        self.thresh = thresh
        self.ratio = ratio

    def next_moves(self):
        pool = ThreadPool()
        moves = pool.map(self._find_move, self.bots)

        return moves

    def _find_move(self, bot):
        def converged(s):
            print(s)
        if stop_fn and stop_fn(bot):
            return [converged, 'Cube {} converged.'.format(bot.mac_address)]
        
        light_values = bot.read_light_sensors()
        sorted_values = sorted(light_values.items(), key=operator.itemgetter(1), reverse=True)
        for face, val in sorted_values:
            if face == 'top' or face == 'bottom':
                continue

            plane = tuple(bot.find_plane())
            if plane == (0, 0, 1) or plane == (0, 0, -1):
                return [bot.change_plane, new_plane]
            elif face == 'forward' or face == 'reverse':
                return [bot.do_action, self._traverse, face]
            else:
                center_d = tuple(bot.find_plane())
                if center_d == (1, 1, 0) or center_d == (-1, -1, 0):
                    new_plane = (1, -1, 0)
                elif center_d == (1, -1, 0) or center_d == (-1, 1, 0):
                    new_plane = (1, 1, 0)
                else:
                    new_plane = (1, 1, 0)

                return [bot.change_plane, new_plane]
