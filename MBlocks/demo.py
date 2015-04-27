from MBlocks.controller import Cube

from itertools import chain, combinations
import random
import thread
import time

do_change = True

def change_color(cube):
    colors = list(chain(combinations('rgb', 1), combinations('rgb', 2)))
    while True:
        for face in range(1, 7):
            color = ''.join(random.sample(colors, 1)[0])
            cube.ser.write(' '.join(('fbrgbled', color, 'tb', str(face))) + '\n')
        time.sleep(2)

def ceo_demo():
    """
    The MAC addresses of the cubes are:
       - 1: C9:6E:6B:9F:96:B6   (mostly red screws)
       - 2: E2:8A:4C:9A:6F:9C   (mostly blue screws)
       - 3: D8:9C:00:41:E4:19   (mostly black screws)

    """
    ports = ['/dev/ttyACM' + str(x) for x in range(1,2)]
    print ports

    cubes = [Cube(port) for port in ports]
    for cube in cubes:
        if cube.mac_address == 'C9:6E:6B:9F:96:B6':
            fst = cube
            fst.disconnect()
        elif cube.mac_address == 'E2:8A:4C:9A:6F:9C':
            scd = cube
        elif cube.mac_address == 'D8:9C:00:41:E4:19':
            lst = cube
            lst.disconnect()

    thread.start_new_thread(change_color, (scd,))
    # fst.ser.write('ia f 10000 3500 5\n')  # Corner climb
    # time.sleep(3)
    # fst.ser.write('ia f 5000 2500 10\n')  # Traverse
    # time.sleep(3)

    # scd.ser.write('ia f 13000 4000 4 e 15\n')  # Vertical climb
    # time.sleep(3)
    # scd.ser.write('ia f 13000 4000 4 e 15\n')  # Vertical convex
    # time.sleep(3)

    # Random motion
    # scd.ser.write('ia f 6000 2500 10\n') # Traverse
    # scd.change_plane('left')

if __name__ == '__m in__':
    ceo_demo()
