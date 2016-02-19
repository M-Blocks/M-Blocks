import csv
import math
import operator
import re
import serial
import string
import sys
import time
import urllib2

from collections import defaultdict

import MBlocks.utils as utils
import numpy as np


class NoCubeException(Exception):
    pass


class TimeoutException(Exception):
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

        try:
            self.config = None
            self.mac_address = self.read_mac_address()
            self.connected = True

            self.__cache = defaultdict(lambda: None)
            self.__calibrate = self._read_calibration()
            self.__configs = self._read_configs()

            self.ser.write('fbrxen 0 1\n')
            self.find_config()

            # Show battery when connecting
        except NoCubeException:
            self.disconnect()
            raise
        except: 
            self.disconnect()
            raise

    def disconnect(self):
        self.connected = False
        self.__cache = defaultdict(lambda: None)
        
        """Disconnect the cube. Also stops the motor and shuts off the lights."""
        if not self.ser.isOpen():
            self.ser.open()
        self.ser.write('blediscon\n')
        self.ser.close()

    def restart(self):
        """Reinitializes the IMU units."""
        self.ser.write('imuinit\n')
        time.sleep(5)
        self.ser.write('atd\n')
        time.sleep(5)

        mac_address = self.read_mac_address()
        while mac_address != self.mac_address:
            time.sleep(5)
            self.ser.write('blediscon\n')
            time.sleep(2)
            self.ser.write('atd\n')
            time.sleep(5)
            mac_address = self.read_mac_address()

    def do_action(self, action, direction):
        """Attempts to perform an action from the calibration table."""
        self.__cache['center'] = None
        self.__cache['face'] = None

        command = self.__calibrate[action, direction]
        self.ser.write(command + '\n')

        timeout = time.time() + 20.0
        while True:
            if time.time() > timeout:
                return
            line = self.ser.readline()
            if 'Successfully' in line or 'Failed' in line:
                print line
                break
            elif 'complete' in line or 'failure' in line:
                print line
                break
        self.ser.flushInput()
        self.ser.flushOutput()

    def change_plane(self, alignment):
        """Change plane to align with a specified alignment.

        :param alignment: One of {(0, 0, 1), (1, 1, 0), (1, -1, 0)}
        """
        planes = [(0, 0, 1), (1, -1, 0), (1, 1, 0)]
        index = planes.index(alignment)
        
        def get_alignment():
            plane = self.find_plane()
            if plane is None:
                return 0, []
            for i, p in enumerate(planes):
                if p == tuple(plane) or p == tuple(-plane):
                    return i, p

        try_num = 0
        i, current = get_alignment()
        while True:
            try_num += 1
            if planes[i] == alignment:
                break
            if (i + 1) % 3 == index:
                self.do_action('change_plane', 'forward')
            else:
                self.do_action('change_plane', 'reverse')
            i, current = get_alignment()
        
        print('Final: {0} (tries: {1})'.format(self.config, try_num))

    def is_connected(self, face, thresh=5):
        # TODO: find better way to do this, as this does not always work
        light = self.read_light_sensor(face)                
        if light < thresh:
            return True

    def send_message(self, face, message):
        self.ser.write('fbirled {}\n'.format(face))
        self.ser.write('fbtxled {} 1\n'.format(face))
        self.ser.write('fbtx {} {}\n'.format(face, message))

    def read_message_length(self, face):
        self.ser.write('fbrxcount {}\n'.format(face))

        timeout = time.time() + 5.0
        while True:
            if time.time() > timeout:
                return 0
            line = self.ser.readline()
            if 'consumed' in line:
                cnt = line.split(':')[1]
                break
        self.ser.flushInput()
        self.ser.flushOutput()

        return int(cnt)
    
    def read_message(self, face, length):
        self.ser.write('fbrx {} {}\n'.format(face, length))

        timeout = time.time() + 5.0
        while True:
            if time.time() > timeout:
                return ''
            line = self.ser.readline()
            if 'Read' in line:
                break
        msg = self.ser.readline()
        self.ser.flushInput()
        self.ser.flushOutput()
        
        return msg

    def read_mac_address(self):
        # Get MAC address of cube (unique)
        found = False
        line = ''

        timeout = time.time() + 5.0
        while True:
            if time.time() > timeout:
                return 'UNKNOWN'
            try:
                line = self.ser.readline()
                if 'CONN' == line[:4]:
                    found = True
                    break
            except serial.serialutil.SerialException:
                pass
        if not found:
            raise NoCubeException
        self.ser.flushInput()
        self.ser.flushOutput()

        return ''.join(line.split()[1].split(':'))

    def find_plane(self):
        grav = self.read_imu('c')
        
        thresh = 10
        planes = np.array([(0, 0, 1), (1, -1, 0), (1, 1, 0)])
        for i, plane in enumerate(planes):
            angle = utils.angle(plane, grav) / math.pi * 180
            if angle < thresh:
                return plane
            elif angle > 180 - thresh:
                return -plane

    def find_angles(self, sensor='c'):
        grav = self.read_imu(sensor)

        planes = np.array([(0, 0, 1), (1, -1, 0), (1, 1, 0)])
        angles = []
        for i, plane in enumerate(planes):
            angle = utils.angle(plane, grav) / math.pi * 180
            angles.append(angle)

        return np.array(angles)

    def read_imu(self, sensor='c'):
        if sensor == 'c' and self.__cache['center']:
            return self.__cache['center']
        if sensor == 'f' and self.__cache['face']:
            return self.__cache['face']
        
        self.ser.write('imuselect {0}\n'.format(sensor))
        self.ser.write('imugravity\n')

        timeout = time.time() + 5.0
        while True:
            if time.time() > timeout:
                return []
            line = self.ser.readline()
            if 'Gravity vector (int)' in line:
                break
        self.ser.flushInput()
        self.ser.flushOutput()
        s, e = line.index('['), line.index(']')
        gravity = [int(x) for x in line[s+1:e].split()]
        
        return gravity

    def read_light_sensor(self, face):
        """Read the light sensor at a face."""
        self.ser.write('fblight {0}\n'.format(face))

        s = 'Faceboard {0} ambient light:'.format(face)

        timeout = time.time() + 5.0
        while True:
            if time.time() > timeout:
                return self._timeout_handler(0)
            line = self.ser.readline()
            if s in line:
                break

        sensor = line.split(':')[1]
        try:
            val = int(sensor.strip())
        except ValueError:
            val = None
        
        self.ser.flushInput()
        self.ser.flushOutput()

        return val

    def read_light_sensors(self):
        """Reads the light sensors at each of the faces and returns a
        dictionary with results.
        """
        self.find_config()
        
        res = {}
        for face in xrange(1, 7):
            res[face] = self.read_light_sensor(face)
        result = {}
        for k, v in self.config.items():
            if k in ('top', 'bottom', 'left', 'right', 'forward', 'reverse'):
                result[k] = res[v]

        return result

    def find_config(self):
        plane_c = self.find_angles('c')
        plane_f = self.find_angles('f')

        if plane_f != []:
            for config in self.__configs:
                dist_c = np.dot(plane_c - config['center'], plane_c - config['center'])
                dist_f = np.dot(plane_f - config['face'], plane_f - config['face'])
                if  dist_c < 10 and dist_f < 10:
                    self.config = config
                    break
        else:
            readings = [self.read_light_sensor(f) for f in range(1, 7)]
            min_light = min(readings)
            for config in self.__configs:
                dist_c = np.dot(plane_c - config['center'], plane_c - config['center'])
                if dist_c < 10 and readings[config['bottom'] - 1] == min_light:
                    self.config = config
                    break

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
            if row[0] == self.mac_address or row[0] == 'DEFAULT':
                direction = row[5].strip()
                for i in range(6, len(labels)):
                    result[labels[i].strip(), direction] = row[i].strip()

        return result
