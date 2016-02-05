import time


class TwoCubeController(object):
    def __init__(self, leader, mover):
        self.leader = leader
        self.mover = mover

    def steer(self, direction='f', speed=3500, brake=2300):
        self.leader.ser.write('bldcspeed f 8000\n')
        time.sleep(4)
        self.leader.ser.write('bldcstop b\n')

    def advance(self, direction='forward'):
        self.mover.do_action('two_cube_traverse', '{0}'.format(direction))
        self.mover.do_action('two_cube_traverse', '{0}'.format(direction))


print 'Hello'
