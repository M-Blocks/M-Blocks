from MBlocks.controller import Cube
from MBlocks.twocube import TwoCubeController


def light_follower_demo():
    port0 = input('Enter port of first cube (e.g. COM3): ')
    port1 = input('Enter port of second cube (e.g. COM4): ')
    cube0 = Cube(port0)
    cube1 = Cube(port1)

    print 'First cube is {0}. Second cube is {1}.'.format(cube0.mac_address, cube1.mac_address)
    leader = input('Enter cube that is steering (1 for first cube, 2 for second cube): ')
    if leader == 1:
        leader, driver = cube0, cube1
    else:
        leader, driver = cube1, cube0
    control = TwoCubeController(leader, driver)

    for i in range(5):
        try:
            face, value = driver.find_strongest_light_signal()
            print face, value
            if face is 'Forward':
                control.drive('f')
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
