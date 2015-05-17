import time


class TwoCubeController(object):
    def __init__(self, leader, mover):
        self.leader = leader
        self.mover = mover

    def steer(self, direction='f', speed=3500, brake=2300):
        self.leader.ser.write('ia {0} {1} {2} 20\n'.format(direction, speed, brake))
        time.sleep(1.5)

    def advance(self, direction='forward'):
        self.mover.do_action('two_cube_traverse', '{0}'.format(direction))
        self.mover.do_action('two_cube_traverse', '{0}'.format(direction))
