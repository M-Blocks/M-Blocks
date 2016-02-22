import numpy as np
import time
import operator


class TwoCubeController(object):
    def __init__(self, fst, scd):
        fst_d = tuple(fst.find_plane())
        if fst_d != (0, 0, 1) and fst_d != (0, 0, -1):
            self.driver = fst
            self.steer = scd
        else:
            self.driver = scd
            self.steer = fst

        # ensure steer is oriented correctly
        self.steer.change_plane((0, 0, 1))
        
        center_d = tuple(self.driver.find_plane())
        if center_d == (0, 0, 1) or center_d == (0, 0, -1):
            # both cubes are oriented with MB parallel to ground
            self.driver.change_plane((1, -1, 0))

        # use light sensor values to check if driver's forward/backward direction is towards steer
        self.driver.find_config()
        center_d = tuple(self.driver.find_plane())
        
        fc, rc = self.driver.config['forward'], self.driver.config['reverse']
        if self.driver.is_connected(fc) or self.driver.is_connected(rc):
            if center_d == (1, 1, 0) or center_d == (-1, -1, 0):
                self.driver.change_plane((1, -1, 0))
            else:
                self.driver.change_plane((1, 1, 0))

        self.config_driver = self.driver.config
        self.config_steer = self.steer.config

    def drive(self):
        """Drive the cube towards the light source.

        Sorts the faces based on their light readings. While the strongest source is not 
        from the front or reverse faces on the driving cube, attempt to steer.

        Steering is done by spinning up the motor to 8000 RPM and then braking. This should
        effectively slide the cube along the ground.
        """ 
        direction = None
        while direction != 'forward' and direction != 'reverse':
            lvalues_steer = self.driver.read_light_sensors(self.config_steer)
            lvalues_driver = self.driver.read_light_sensors(self.config_driver)
            
            sorted_values = sorted(light_values.items(), key=operator.itemgetter(1), reverse=True)
            for k, v in sorted_values:
                if k == 'top' or k == 'bottom':
                    continue

                if lvalues_steer['left'] > v or lvalues_steer['right'] > v:
                    self.steer_cubes()
                elif k == 'forward':
                    direction = 'forward'
                elif k == 'reverse':
                    direction = 'reverse'
                else:
                    self.steer_cubes()

        # TODO: add check to see if both actions were successfully completed
        self.driver.do_action('two_cube_traverse', '{}'.format(direction))
        self.driver.do_action('two_cube_traverse', '{}'.format(direction))

        # We are OK if either both actions completed, or if neither did
        center = tuple(self.steer.find_plane())
        while center != (0, 0, 1):
            # only one move successfully completed
            self.driver.do_action('two_cube_traverse', '{}'.format(direction))

        self._flip_configs()

    def steer_cubes(self, sleep=4):
        # find whether direction is clockwise or counterclockwise to center ring
        light_values = [self.steer.read_light_sensor(face) for face in self.steer['ring']]
        min_val = min(light_values)
        id = light_values.index(min_val)
        
        if light_values[id - 1] > light_values[(id + 1) % 4]:  # counterclockwise motion
            self.steer.write('bldcspeed r 8000\n')
        else:                                                  # clockwise motion
            self.steer.write('bldcspeed f 8000\n')
        time.sleep(sleep)
        self.steer.ser.write('bldcstop b\n')

    def _flip_configs():
        config_d = self.config_driver
        config_d['forward'] = self.config_driver['reverse']
        config_d['reverse'] = self.config_driver['forward']
        config_d['top'] = self.config_driver['bottom']
        config_d['bottom'] = self.config_driver['top']
        self.config_driver = config_d
        
        config_s = self.config_steer
        config_s['left'] = self.config_steer['right']
        config_s['right'] = self.config_steer['left']
        config_s['top'] = self.config_steer['bottom']
        config_s['bottom'] = self.config_steer['top']
        self.config_steer = config_s
