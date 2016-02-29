from MBlocks.control.controller import *

from multiprocessing.dummy import Pool as ThreadPool

class Planner(object):
    def __init__(self, bots, stop_fn):
        self.bots = bots
        self.stop_fn = stop_fn

    def next_moves(self):
        pass

    def execute_moves(self, moves):
        def act(args):
            args[0](*args[1:])

        pool = ThreadPool(len(moves))
        pool.map_async(act, moves)

        pool.close()
        pool.join()

    def add_bot(self, bot):
        for b in self.bots:
            if b.mac_address == bot.mac_address:
                return
            
        self.bots.append(bot)
        
    def remove_bot(bot):
        id = -1
        for i, b in enumerate(self.bots):
            if b.mac_address == bot.mac_address:
               id = i
               break
        if id == -1:
            return
        else:
            self.bots.pop(id)
