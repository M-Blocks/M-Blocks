from itertools import izip

import csv
import fcntl
import math
import os
import random
import re
import serial
import time
import urllib2

import utils

class NoCubeException(Exception):
    pass

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
        found = False
        line = ''
        for i in range(10):
            try:
                line = self.ser.readline()
                if 'CONN' == line[:4]:
                    found = True
                    break
            except serial.serialutil.SerialException:
                pass
        if not found:
            raise NoCubeException
        self.mac_address = line.split()[1]
        self.ser.readline()

        self.ser.flushInput()
        self.ser.flushOutput()

        self.reverse = False
        self.neighbours = []

        self._left = {1: True, 2: False, -1: False, -2: True}
        self._right = {1: False, 2: True, -1: True, -2: False}

        # Forward is the along the positive x-axis
        self.direction = [1, 0]

        self.__calibrate = self._read_calibration()
        self.__configs = self._read_configs()

    def disconnect(self):
        """Disconnect a serial connection.

        :param ser: Serial connector to disconnect.
        :type ser: serial.Serial.
        """
        if not self.ser.isOpen():
            self.ser.open()
        self.ser.write('blediscon\n')
        self.ser.close()

    def move_towards(self, face):
        config = self._find_config()
        if config['Forward'] == face or config['Top'] == face:
            # TODO: Make context specific based on neighbors
            self.move('forward', 6000, 2300, 20)
        elif config['Backward'] == face or config['Bottom'] == face:
            self.move('backward', 6000, 2300, 20)
        elif config['Left'] == face:
            self.change_plane('left')
            self.move('forward', 6000, 2300, 20)
        else:
            self.change_plane('right')
            self.move('forward', 6000, 2300, 20)

    def do_action(self, direction, action):
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

        before, after = {}, {}

        while before == after:
            before = self._find_config()
            self.ser.write(forward)
            time.sleep(3)
            after = self._find_config

    def change_plane(self, direction):
        """Change plane to align with a specified direction.

        :param direction: One of {Left, Right, Top}.
        """
        config = self._find_config()
        if direction is 'Top':
            face = 0
        else:
            face = config[direction]

        forward = 'cp b f 4000 50\n'
        reverse = 'cp b r 4000 50\n'

        try_num = 0
        while config['Forward'] != face:
            orient = abs(self.orientation)
            if config['Left'] == face:
                self.ser.write(forward)
            else:
                self.ser.write(reverse)
            time.sleep(15)
            config = self._find_config()

            try_num += 1

        self.ser.flushInput()
        self.ser.flushOutput()
        print 'Final: {0} (tries: {1})'.format(self.orientation,
                try_num)

    def lattice_planner(self, state, goal):
        while state != goal:
            dx, dy = (goal[i] - state[i] for i in range(2))
            dirx, diry = self.direction

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
                    self.change_plane('Left')
                    state[0] -= sgnx

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

    def _read_configs(self):
        """Read configuration information from Google Drive.
        """
        with open('cube_config.csv', 'rb') as csvfile:
            cr = csv.reader(csvfile)

            result = []
            labels = next(cr)
            for row in cr:
                config = {}
                for label, d in zip(labels, row):
                    config[label] = tuple(int(x) for x in d.strip().split(','))
                    if len(config[label]) == 1:
                        config[label] = config[label][0]
                result.append(config)

        return result

    def _read_calibration(self):
        """ Read calibration from Google Drive.
        """
        url = 'http://docs.google.com/feeds/download/spreadsheets/Export?key=14VPabCGN6TftpdID9zgbFzsRx3mHq_iayQP6OTUrr3A&exportFormat=csv&gid=0'
        response = urllib2.urlopen(url)
        cr = csv.reader(response)

        result = {}
        labels = next(cr)
        for row in cr:
            if row[0] == self.mac_address:
                direction = row[2]
                for i in range(3, 14):
                    result[labels[i]] = row[i].strip()

        return result

    def _read_imu(self, sensor):
        self.ser.write('imuselect {0}\n'.format(sensor))
        self.ser.write('imugravity\n')
        while True:
            line = self.ser.readline()
            if 'Active IMU' in line:
                break

        lines = [self.ser.readline() for i in range(5)]
        alpha = float(re.findall('\d+.\d+', lines[2])[-1])
        beta = float(re.findall('\d+.\d+', lines[3])[-1])
        gamma = float(re.findall('\d+.\d+', lines[4])[-1])

        return alpha, beta, gamma

    def _find_config(self):
        c_alpha, c_beta, c_gamma = self._read_imu('c')
        f_alpha, f_beta, f_gamma = self._read_imu('f')

        MAX_ERROR = 10
        central_label = 'Central Alignment'
        face_label = 'Face Alignment'
        for config in self.__configs:
            conf_c_alpha, conf_c_beta, conf_c_gamma = config[central_label]
            conf_f_alpha, conf_f_beta, conf_f_gamma = config[face_label]

            if abs(c_alpha - conf_c_alpha) < MAX_ERROR and \
               abs(c_beta - conf_c_beta) < MAX_ERROR and \
               abs(c_gamma - conf_c_gamma) < MAX_ERROR and \
               abs(f_alpha - conf_f_alpha) < MAX_ERROR and \
               abs(f_beta - conf_f_beta) < MAX_ERROR and \
               abs(f_gamma - conf_f_gamma) < MAX_ERROR:
                return config
