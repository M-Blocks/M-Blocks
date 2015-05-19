from MBlocks.controller import Cube
from MBlocks.twocube import TwoCubeController


def light_follower_demo():
    print 'Light Follower Demo'
    print '==================='
    print ''
    print 'Follows a light source using two cubes.'
    print 'One of the cubes acts as a steering wheel, while the other provides sensing and driving.'
    print ''

    port0 = input('Enter port of first cube (e.g. \'COM3\'): ')
    port1 = input('Enter port of second cube (e.g. \'COM4\'): ')
    cube0 = Cube(port0)
    cube1 = Cube(port1)

    print '\n-------------'
    print 'First cube is {0}.\nSecond cube is {1}.'.format(cube0.mac_address, cube1.mac_address)
    print '-------------'
    print ''

    leader = input('Enter cube that is steering (1 for first cube, 2 for second cube): ')
    print ''

    if leader == 1:
        leader, driver = cube0, cube1
    else:
        leader, driver = cube1, cube0
    control = TwoCubeController(leader, driver)

    max_value = 0
    EPS = 20
    for i in range(10):
        try:
            face, value = driver.find_strongest_light_signal()
            max_value = max(max_value, value)
            print face, value
            if face == 'Forward' and value >= max_value - EPS:
                control.advance('forward')
            # elif face is 'Backward':
            #    control.drive('r')
            else:
                control.steer()
        except:
            leader.disconnect()
            driver.disconnect()
            break

    leader.disconnect()
    driver.disconnect()

if __name__ == '__main__':
    light_follower_demo()
