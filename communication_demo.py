import random
import time

from itertools import *
from MBlocks.controller import Cube


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))


def communication_demo():
    print 'Communication Demo'
    print '==================='
    print ''
    print 'Shows communication between two cubes by alternating blinking lights.'

    port0 = input('Enter port of first cube (e.g. \'COM3\'): ')
    port1 = input('Enter port of second cube (e.g. \'COM4\'): ')
    cube0 = Cube(port0)
    cube1 = Cube(port1)

    print '\n-------------'
    print 'First cube is {0}.\nSecond cube is {1}.'.format(cube0.mac_address, cube1.mac_address)
    print '-------------'
    print ''

    leader = input('Enter cube that is leader (1 for first cube, 2 for second cube): ')
    print ''

    if leader == 1:
        leader, follower = cube0, cube1
    else:
        leader, follower = cube1, cube0

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

if __name__ == '__main__':
    communication_demo()
