from itertools import izip

import csv
import math
import os
import random
import serial
import time
import urllib2

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
        # self.read_calibration()

    def do_action(direction, action):
        command = self.__calibrate[action, direction]
        self.ser.write(command + '\n')

    def move(self, direction, rpm=None, br=None, t=None):
        """Move cube in specified direction.

        Note that this only works for traversal moves.

        :param direction: One of {left, right, forward, backward, up,
            down}; case insensitive.
        """
        forward = 'ia f {0} {1} {2}\n'.format(rpm, br, t)
        reverse = 'ia r {0} {1} {2}\n'.format(rpm, br, t)

        if direction not in ('forward', 'backward'):
            self.change_plane(direction)

        if self.reverse:
            forward, reverse = reverse, forward
        if direction is 'backward':
            forward, reverse = reverse, forward

        before, after = 0, 0

        while before == after:
            self.get_orientation()
            before = self.orientation
            self.ser.write(forward)
            time.sleep(3)
            self.get_orientation()
            after = self.orientation

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
                if '(int)' in line:
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

    def lattice_planner(self, state, goal):
        while state != goal:
            dx, dy = (goal[i] - state[i] for i in range(2))
            dirx, diry = self.direction

            previous_orientation = self.orientation

            sgnx = utils.sgn(dx)
            sgny = utils.sgn(dy)
            if dx != 0:
                state[0] += sgnx
                print 'State: {0}'.format(state)
                if dirx == sgnx:
                    self.move('forward', 5000, 2000, 20)
                elif dirx != 0 and dirx != sgnx:
                    self.move('backward', 5000, 2000, 20)
                elif dirx == 0:
                    self.change_plane('left')
                    state[0] -= sgnx

                self.get_orientation()
                if self.orientation == previous_orientation:
                    print 'Failure'
                    state[0] -= dy

            elif dy != 0:
                state[1] += sgny
                print 'State: {0}'.format(state)
                if diry == sgny:
                    self.move('forward', 5000, 2000, 20)
                elif diry != 0 and diry != sgny:
                    self.move('backward', 5000, 2000, 20)
                elif diry == 0:
                    self.change_plane('left')
                    state[1] -= sgny

                self.get_orientation()
                if self.orientation == previous_orientation:
                    print 'Failure'
                    state[1] -= dy

    def read_calibration(self):
        """ Read calibration from Google Drive.
        """
        url = 'http://docs.google.com/feeds/download/spreadsheets/Export?key=14VPabCGN6TftpdID9zgbFzsRx3mHq_iayQP6OTUrr3A&exportFormat=csv&gid=0'
        response = urllib2.urlopen(url)
        cr = csv.reader(response)

        labels = next(cr)
        for row in cr:
            if row[0] == self.mac_address:
                direction = row[2]
                for i in range(3, 14):
                    self.__calibrate[labels[i]] = row[i].strip()
