import numpy as np
import time
import operator


class TwoCubeController(object):
    central_label = 'Central Alignment'
    
    def __init__(self, fst, scd):
        if fst.config[central_label] != (0, 0, 1):
            self.driver = fst
            self.steer = scd
        else:
            self.driver = scd
            self.steer = fst

        # ensure steer is oriented correctly
        self.steer.change_plane((0, 0, 1))
        center_d = self.driver.config[central_label]
        center_s = self.steer.config[central_label]
        if np.all(np.absolute(center_d) == (0, 0, 1)):
            # both cubes are oriented with MB parallel to ground
            self.driver.change_plane((1, 1, 0))

        # TEMP: use light sensor values to check if driver's forward/backward direction is towards steer
        self.driver._find_config()
        center_d = self.driver.config[central_label]
        
        lights = self.driver._read_light_sensors()
        if light_values['Forward'] == 0 or light_values['Backward'] == 0:
            if center_d == (1, 1, 0) or center_d == (-1, -1, 0):
                self.driver.change_plane((1, -1, 0))
            else:
                self.driver.change_plane((1, 1, 0))

    def drive(self):
        """Drive the cube towards the light source.

        Sorts the faces based on their light readings. While the strongest source is not 
        from the front or reverse faces on the driving cube, attempt to steer.

        Steering is done by spinning up the motor to 8000 RPM and then braking. This should
        effectively slide the cube along the ground.
        """ 
        direction = None
        while direction != 'forward' and direction != 'reverse':
            light_values = self.driver._read_light_sensors()
            sorted_values = sorted(light_values.items(), key=operator.itemgetter(1), reverse=True)
            for k, v in sorted_values:
                if k == 'Top' or k == 'Bottom':
                    continue
                if k == 'Forward':
                    direction = 'forward'
                elif k == 'Backward':
                    direction = 'reverse'
                elif sorted_values['Forward'] > sorted_values['Backward']:
                    self.steer(direction='f')
                else:
                    self.steer(direction='r')

        # TODO: add check to see if both actions were successfully completed
        self.leader.do_action('two_cube_traverse', '{}'.format(direction))
        self.leader.do_action('two_cube_traverse', '{}'.format(direction))

        # We are OK if either both actions completed, or if neither did
        self.driver._find_config()
        center = self.driver.config[central_label]
        while np.any(np.absolute(center) != (0, 0, 1)):
            # only one move successfully completed
            self.leader.do_action('two_cube_traverse', '{}'.format(direction))

    def steer(self, direction):
        self.leader.ser.write('bldcspeed {} 8000\n'.format(direction))
        time.sleep(4)
        self.leader.ser.write('bldcstop b\n')

