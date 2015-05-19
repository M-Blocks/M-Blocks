import random
import time
import threading

from itertools import *
from threading import Thread
from MBlocks.controller import Cube
from MBlocks.twocube import TwoCubeController


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))


def light_follower_demo(leader, driver):
    control = TwoCubeController(leader, driver)

    max_value = 0
    EPS = 20
    for i in range(10):
        try:
            face, value = driver.find_strongest_light_signal()
            print face, value
            if face == 'Forward' and value >= max_value - EPS:
                control.advance('forward')
            # elif face is 'Backward':
            #    control.drive('r')
            else:
                control.steer()

            max_value = max(max_value, value)
        except:
            leader.disconnect()
            driver.disconnect()
            break

    leader.disconnect()
    driver.disconnect()


def communication_demo(leader, follower):
    colors = list(powerset('rgb'))

    for i in range(10):
        color = ''.join(random.choice(colors))
        leader.ser.write('fbrgbled {0} tb 1 2 3 4 5 6\n'.format(color))

        time.sleep(1)
        msg = 'x' + color
        leader.send_message(1, msg)
        r_msg = follower.read_message(1, len(msg))
        if len(r_msg) < len(msg):
            follower.ser.write('fbrgbled {0} tb 1 2 3 4 5 6\n'.format(color))
        else:
            follower.ser.write('fbrgbled {0} tb 1 2 3 4 5 6\n'.format(color))
        time.sleep(5)

    leader.ser.write('fbrgbled off tb 1 2 3 4 5 6\n')
    follower.ser.write('fbrgbled off tb 1 2 3 4 5 6\n')

    leader.disconnect()
    follower.disconnect()


def traversal_demo(cube):
    for i in range(5):
        cube.do_action('traverse', 'forward')
        cube.do_action('traverse', 'forward')
        # cube.do_action('traverse', 'forward')

        cube.do_action('traverse', 'reverse')
        cube.do_action('traverse', 'reverse')
        # cube.do_action('traverse', 'reverse')


def change_color_demo(cube):
    colors = list(powerset('rgb'))

    for i in range(10):
        color = ''.join(random.choice(colors))
        cube.ser.write('fbrgbled {0} tb 1 2 3 4 5 6\n'.format(color))

def demo_all(ports):
    cubes = [Cube(port) for port in ports]
    for i, cube in enumerate(cubes):
        print 'Cube {0}: {1}'.format(i, cube.mac_address)

    light_fst = int(input('Enter light following cube #1: '))
    # light_scd = int(input('Enter light following cube #2: '))

    # comms_fst = int(input('Enter comms cube #1: '))
    # comms_scd = int(input('Enter comms cube #2: '))

    traverse1 = int(input('Enter traversal cube #1: '))
    traverse2 = int(input('Enter traversal cube #2: '))

    threading.Thread(target=change_color_demo, args=(cubes[light_fst],)).start()
    # threading.Thread(target=change_color_demo, args=(cubes[light_scd],)).start()
    # threading.Thread(target=communication_demo, args=(cubes[comms_fst], cubes[comms_scd])).start()
    threading.Thread(target=traversal_demo, args=(cubes[traverse1],)).start()
    threading.Thread(target=traversal_demo, args=(cubes[traverse2],)).start()
    # threading.Thread(target=change_color_demo, args=(cubes[color_cube],)).start()

if __name__ == '__main__':
    demo_all(['com7', 'com8', 'com9'])
