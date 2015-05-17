import time


class TwoCubeController(object):
    def __init__(self, leader, mover):
        self.leader = leader
        self.mover = mover

    def steer(self, direction='f', speed=3000, brake=1000):
        self.leader.ser.write('ia {0} {1} {2} 20\n'.format(direction, speed, brake))

    def advance(self, direction='forward'):
        self.mover.do_action('traverse', '{0}'.format(direction))
        self.mover.do_action('traverse', '{0}'.format(direction))
