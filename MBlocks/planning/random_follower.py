from MBlocks.planning.planner import Planner

from collections import defaultdict

class RandomLightPlanner(Planner):
    def __init__(self, bots, thresh=100, ratio=0.8,
                     traverse='traverse'):
        super(RandomLightPlanner, self).__init__(bots)

        self.thresh = thresh
        self.ratio = ratio

        self._traverse = traverse
        self.state = defaultdict(lambda: None)

    def next_moves(self):
        moves = []
        for bot in self.bots:
            lights = bot.read_light_sensors()

            ratio = min(lights['forward']/float(lights['reverse']), lights['reverse']/float(lights['forward']))
            if ratio > self.ratio:
                # if forward and reverse are almost the same, do random move
                moves.append(self.find_move(bot))
            elif lights['forward'] > lights['reverse']:
                moves.append([bot.do_action, self._traverse, 'forward'])
            else:
                moves.append([bot.do_action, self._traverse, 'reverse'])

        return moves

    def find_move(self, bot):
        center = tuple(bot.read_imu('c'))
        if center == (0, 0, 1) or center == (0, 0, -1):
            return [bot.ser.write, 'bldcaccel f 10000 50\n']
        else:
            return [bot.ser.write, 'cp b f 5000 50\n']
