from multiprocessing.dummy import Pool as ThreadPool

class AsyncPlanner(object):
    def __init__(self, bots, planner, **kwargs):
        self.steps = 1
        self.planners = []
        for bot in bots:
            self.planners.append(planner([bot], **kwargs))

    def run_steps(self, steps=1):
        self.steps = steps
        
        pool = ThreadPool()
        pool.map_async(self._run, self.planners)

        pool.close()
        pool.join()

    def _run(self, planner):
        for i in range(self.steps):
            moves = planner.next_moves()
            planner.execute_moves(moves)
