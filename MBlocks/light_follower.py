from MBlocks.controller import *

from multiprocessing.dummy import Pool as ThreadPool 

def move(args):
    args[0].move_towards(args[1])

def change_plane(args):
    args[0].change_plane(args[1])

def light_follower_demo(seed, cubes, thresh=90, ratio=0.7):
    found = True

    for cube in cubes:
        cube._find_config()

    while True:
        time.sleep(5)
        face, max_value = seed.light_follower(thresh, ratio)
        if face is None:
            break
        if face in ('Forward', 'Backward'):
            seed.move_towards(face)
        elif face in ('Left', 'Right'):
            seed.change_plane(face)

    while found:
        found = False
        found_mover = False

        movers = []
        changers = []
        best_mover, best_value, best_dir = None, 0, None
        for cube in cubes:
            face, max_value = cube.light_follower(0, 1)
            if face is None:
                continue
            if face in ('Forward', 'Backward'):
                movers.append((cube, face))
                if best_value < max_value:
                    best_mover, best_value, best_dir = cube, max_value, face
            elif face in ('Left', 'Right'):
                changers.append((cube, face))
            found = True

        # if best_mover is not None:
            # movers = [(best_mover, best_dir)]
        if movers or changers:
            pool = ThreadPool(len(cubes))
            pool.map_async(move, movers)
            pool.map_async(change_plane, changers)

            pool.close()
            pool.join()
