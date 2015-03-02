from itertools import izip

import csv
import math
import os
import random
import serial
import time

import utils

class Cube(object):
    def __init__(self, port, baud=115200):
        """Connect to a serial port at a given baud rate.

        :param port: Port number to connect to.
        :type port: str.
        :param baud: Baud rate (default 115200).
        :type baud: int.
        """
        self.ser = serial.Serial(port, baud, timeout=1)
        self.ser.write('atd\n')

        # Get MAC address of cube (unique)
        line = ''
        while True:
            try:
                line = self.ser.readline()
                if 'CONN' == line[:4]:
                    break
            except serial.serialutil.SerialException:
                pass
        self.mac_address = line.split()[1]

        self.orientation = 0
        self.reverse = False

        self.neighbours = []

        self._left = {1: True, 2: False, -1: False, -2: True}
        self._right = {1: False, 2: True, -1: True, -2: False}

        # Forward is the along the positive x-axis
        self.direction = [1, 0]

        self.__calibrate = {}
        self.read_calibration()

    def _move(self, direction, rpm, br, t):
        """Move cube in specified direction.

        :param direction: One of {left, right, forward, backward, up,
            down}; case insensitive.
        """
        # TODO: Only moves it along the xy-plane

        forward = 'ia f {0} {1} {2}\n'.format(rpm, br, t)
        reverse = 'ia r {0} {1} {2}\n'.format(rpm, br, t)

        if direction not in ('forward', 'backward'):
            self.change_plane(direction)

        if self.reverse:
            forward, reverse = reverse, forward
            if direction is 'backward':
                forward, reverse = reverse, forward

        self.get_orientation()
        before = self.orientation

        self.ser.write(forward)
        time.sleep(5)

        self.get_orientation()
        after = self.orientation

        if before != after:
            return True
        else:
            return False

    def disconnect(self):
        """Disconnect a serial connection.

        :param ser: Serial connector to disconnect.
        :type ser: serial.Serial.
        """
        if not self.ser.isOpen():
            self.ser.open()
        self.ser.write('blediscon\n')
        self.ser.close()

    def get_orientation(self):
        """Determine orientation of cube.
        """
        if not self.ser.isOpen():
            self.ser.open()
        self.ser.write('imugravity\n')

        line = ''
        while True:
            try:
                line = self.ser.readline()
                if 'Gravity:' in line:
                    break
            except serial.serialutil.SerialException:
                pass

        s, e = line.index('['), line.index(']')
        grav = [int(x) for x in line[s+1:e].split()]

        thresh = 10
        planes = [[0, 0, 1], [0.707107, -0.707107, 0], [0.707107,
            0.707107, 0]]

        for i, plane in enumerate(planes):
            angle = utils.angle(plane, grav) / math.pi * 180
            if angle < thresh:
                self.orientation = i
                break
            elif angle > 180 - thresh:
                self.orientation = -i
                break

    def change_plane(self, direction):
        """Change plane to align with a specified direction.

        :param direction: One of {left, right, up, down}. A plane
            corresponds to two directions: one for each
            of (left, right) and (up, down).
        """
        forward = 'cp b f 1000 5\n'
        reverse = 'cp b r 1000 5\n'

        # Need to check if connected to cube and want to move sideways
        self.get_orientation()
        if abs(self.orientation) == 1:
            d = 2
        elif abs(self.orientation) == 2:
            d = 1
        else:
            d = 0

        # Check if forward direction should be reversed
        if direction is 'left' and self._left[self.orientation]:
            self.reverse = not self.reverse
        elif direction is 'right' and self._right[self.orientation]:
            self.reverse = not self.reverse

        # Determine direction of forward vector
        if direction is 'left':
            self.direction = utils.rotate(self.direction, math.pi/2)
        if direction is 'right':
            self.direction = utils.rotate(self.direction, -math.pi/2)

        print 'Direction: {0}'.format(self.direction)

        print 'Current: {0}'.format(self.orientation)
        print 'Desired: {0}'.format(d)

        try_num = 0
        while abs(self.orientation) != d:
            orient = abs(self.orientation)
            if (orient + 1) % 3 == d:
                self.ser.write(forward)
            else:
                self.ser.write(reverse)
            time.sleep(15)
            self.get_orientation()

            try_num += 1

        print 'Final: {0} (tries: {1})'.format(self.orientation,
                try_num)

    def do_action(self, action, direction):
        """ Perform an action in a specified direction.

        Reads from the configuration map.

        :param action: Action the cube will take.
        :param direction: Direction to move in.
        """
        rpm, br, t = self.__calibrate[action, direction]
        if direction == 'forward':
            d = 'f'
        else:
            d = 'r'

        self.ser.write('ia {0} {1} {2} {3}\n'.format(d, rpm, br, t))
        time.sleep(5)

    def lattice_planner(self, state, goal):
        """ Move from current position to goal position on a regular lattice.

        :param state: Current state of the system.
        :param goal: Goal position.
        """
        while state != goal:
            dx, dy = (goal[i] - state[i] for i in range(2))
            dirx, diry = self.direction

            sgnx = utils.sgn(dx)
            sgny = utils.sgn(dy)
            if dx != 0:
                state[0] += sgnx
                print 'State: {0}'.format(state)
                if dirx == sgnx:
                    self.do_action('traverse', 'forward')
                elif dirx != 0 and dirx != sgnx:
                    self.do_action('traverse', 'backward')
                elif dirx == 0:
                    self.change_plane('left')
                    state[0] -= sgnx

            elif dy != 0:
                state[1] += sgny
                print 'State: {0}'.format(state)
                if diry == sgny:
                    self.do_action('traverse', 'forward')
                elif diry != 0 and diry != sgny:
                    self.do_action('traverse', 'backward')
                elif diry == 0:
                    self.change_plane('left')
                    state[1] -= sgny

    def plan(self, state, goal, stimulus, update, good_enough):
        """Plan a trajectory for the robot to move from the current
        state to the goal under a given stimulus function.

        Example: move from the current position towards a light source
        until the light stimulus is over a threshold (the goal).

        :param state: Current state of the robot.
        :param goal: Goal state of the robot.
        :param stimulus: Stimulus function that gives an updated state
            after the robot moves.
        :param update: Update the state to the new state of the
            system.
        :param good_enough: Function that returns True if the current
            state is close enough to the goal.
        """
        while not good_enough(state, goal):
            direction = stimulus(state, goal)
            self.do_action('traverse', direction)
            state = update(state, direction)

    def calibrate(self, action, direction='forward'):
        """ Calibrate parameters for IA.

        :param action: Action the block will take (see Table 2)
        :param direction: Direction the action is taken in (forward or reverse)

        TODO: Make this task based
        """
        valid_dirs = ['forward', 'backward']
        valid_acts = ['traverse', 'horizontal_traverse', 'vertical_traverse',
                      'horizontal_convex', 'vertical_convex',
                      'horizontal_concave', 'vertical_concave',
                      'corner_climb', 'stair_step']

        if direction not in valid_dirs:
            raise ValueError('Invalid direction: {0}'.format(direction))
        if action not in valid_acts:
            raise ValueError('Invalid action: {0}'.format(action))

        t = 250
        min_rpm, max_rpm = 1000, 15000
        min_br, max_br = 500, 5000

        for rpm in xrange(min_rpm, max_rpm, 500):
            for br in xrange(min_br, max_br, 500):
                print rpm, br
                if self._move(direction, rpm, br, t):
                    print "Success!"
                    # Attempt same command 3 more times
                    for i in xrange(3):
                        if not self._move(direction, rpm, br, t):
                            break
                    else:
                        self.__calibrate[action, direction] = (rpm,
                                                               br,
                                                               t)
                        return

    def write_calibration(self):
        """ Write calibration to a file.

        The filename is the same as the MAC address of the cube.
        """
        filename = self.mac_address.replace(":", "")
        with open(filename, 'wb') as f:
            for k, v in self.__calibrate.items():
                f.write('{0},{1},{2},{3},{4}\n'.format(k, *v))

    def read_calibration(self):
        """ Read calibration from file.

        The filename is the same as the MAC address of the cube.
        If the file is not found, nothing happens.
        """
        filename = self.mac_address.replace(":", "")
        if os.path.isfile("./" + filename):
            with open(filename, 'rb') as f:
                csvreader = csv.reader(f, delimiter=',')
                for row in csvreader:
                    self.__calibrate[row[0],row[1]] = row[2:]
        print self.__calibrate
