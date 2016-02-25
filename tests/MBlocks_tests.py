from MBlocks.control.controller import Cube

def test_traverse(cube, runs):
    for i in range(runs):
        cube.do_action('traverse', 'forward')
    for i in range(runs):
        cube.do_action('traverse', 'reverse')
