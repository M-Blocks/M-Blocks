def puzzle(cubes, src, dst):
    done = False

    while not done:
        directions = []
        deltas = []
        for s, t in zip(src, dst):
            if s[0] > t[0]:
                deltas.append((-1,0,0))
                directions.append('backward')
            elif s[0] < t[0]:
                deltas.append((1,0,0))
                directions.append('forward')
            elif s[1] > t[1]:
                deltas.append((0,-1,0))
                directions.append('left')
            elif s[1] < t[1]:
                deltas.append((0,1,0))
                directions.append('right')
            else:
                deltas.append((0,0,0))
                directions.append(None)

        for cube, d in zip(cubes, directions):
            if d is not None:
                cube.do_action('traverse', d)

        for i in range(len(deltas)):
            src[i] = utils.add(deltas[i], src[i])

        done = True
        for s, t in zip(src, dst):
            if s != t:
                done = False
