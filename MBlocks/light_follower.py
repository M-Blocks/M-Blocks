from MBlocks.controller import *

from multiprocessing.dummy import Pool as ThreadPool 

def move(args):
    args[0].move_towards(args[1])

def change_plane(args):
    args[0].change_plane(args[1])

def light_follower_demo(cubes):
    found = True
    while found:
        found = False
        found_mover = False

        movers = []
        changers = []
        for cube in cubes:
            face = cube.light_follower()
            if face is None:
                continue
            if face in ('Forward', 'Backward') and not found_mover:
                movers.append((cube, face))
                found_mover = True
            elif face in ('Left', 'Right'):
                changers.append((cube, face))
            found = True

        if movers or changers:
            pool = ThreadPool(len(cubes))
            pool.map(move, movers)
            pool.map(change_plane, changers)

            pool.close()
            pool.join()
