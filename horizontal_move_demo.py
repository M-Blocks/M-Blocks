from MBlocks.controller import Cube


def horizontal_move_demo():
    print('Horizontal Move Demo')
    print('====================')
    print('')
    print('Moves the cube using horizontal traverse moves.')
    print('Press Ctrl-C to stop the demo.')
    print('')

    port = input('Enter port name (e.g. \'COM3\'): ')
    cube = Cube(port)

    print('\n-------------')
    print('Connected to cube {0}'.format(cube.mac_address))
    print('-------------')
    while True:
        cube.do_action('horizontal_traverse', 'forward')

if __name__ == '__main__':
    horizontal_move_demo()
