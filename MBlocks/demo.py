from MBlocks.controller import Cube

from itertools import chain, combinations
import random
import thread
import time

do_change = True

def change_color(cube):
    colors = list(chain(combinations('rgb', 1), combinations('rgb', 2)))
    for i in range(60):
        for face in range(1, 7):
            color = ''.join(random.sample(colors, 1)[0])
            cube.ser.write(' '.join(('fbrgbled', color, 'tb', str(face))) + '\n')
        time.sleep(2)

def stop_color(cube):
    cube.ser.write('fbrgbled off tb 1 2 3 4 5 6\n')

def ceo_demo_temp(ports):
    cubes = [Cube(port) for port in ports]

    time.sleep(5)
    for i in range(3):
        for j in range(2):
            for cube in cubes:
                cube.ser.write('ia f 6000 1800 20\n')
            time.sleep(5)
        for j in range(2):
            for cube in cubes:
                cube.ser.write('ia r 6000 1900 20\n')
            time.sleep(5)

    for cube in cubes:
        cube.disconnect()

def ceo_demo(ports):
    """
    The MAC addresses of the cubes are:
       - 1: E2:8A:4C:9A:6F:9C   (mostly blue screws)
       - 2: D8:9C:00:41:E4:19   (mostly black screws)
    """
    cubes = [Cube(port) for port in ports]
    for cube in cubes:
        thread.start_new_thread(change_color, (cube,))

    for i in range(3):
        for j in range(2):
            for cube in cubes:
                cube.ser.write('ia f 6000 1300 20\n')
            time.sleep(3)
        for j in range(2):
            for cube in cubes:
                cube.ser.write('ia f 6000 1500 20\n')
            time.sleep(3)

if __name__ == '__m in__':
    ceo_demo()
