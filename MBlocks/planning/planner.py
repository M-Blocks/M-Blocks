from MBlocks.control.controller import *

from multiprocessing.dummy import Pool as ThreadPool

class Planner(object):
    def __init__(self, bots):
        self.bots = bots

    def next_moves(self):
        pass

    def execute_moves(self, moves):
        def act(args):
            args[0](*args[1:])

        pool = ThreadPool(len(moves))
        pool.map_async(act, moves)

        pool.close()
        pool.join()
