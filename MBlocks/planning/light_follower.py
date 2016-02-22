import operator

from MBlocks.planning.planner import Planner

class LatticeLightPlanner(Planner):
    def __init__(self, bots, thresh=100, ratio=0.7,
                     traverse='traverse', change='change_plane'):
        super(LatticeLightPlanner, self).__init__(bots)

        self._traverse = traverse
        self._change = change
        
        self.thresh = thresh
        self.ratio = ratio

    def next_moves(self):
        def complete_aux(name):
            print('Cube {} has reached the destination.'.format(name))
            
        moves = []
        for bot in self.bots:
            light_values = bot.read_light_sensors()
            sorted_values = sorted(light_values.items(), key=operator.itemgetter(1), reverse=True)

            if sorted_values[0][1] > thresh:
                moves.append([complete_aux, bot.mac_address])
                continue
            
            for face, val in sorted_values:
                if face == 'top' or face == 'bottom':
                    continue
                if face == 'forward' or face == 'reverse':
                    moves.append([bot.do_action, self._traverse, face])
                else:
                    center_d = tuple(bot.find_plane())
                    if center_d == (1, 1, 0) or center_d == (-1, -1, 0):
                        new_plane = (1, -1, 0)
                    elif center_d == (1, -1, 0) or center_d == (-1, 1, 0):
                        new_plane = (1, 1, 0)
                    else:
                        new_plane = (1, 1, 0)
                        
                    moves.append([bot.change_plane, new_plane])

        return moves
