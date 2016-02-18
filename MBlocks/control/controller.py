import csv
import math
import operator
import re
import serial
import string
import sys
import time
import threading
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

            self._timeout_fn = lambda: None
            self.__cache = defaultdict(lambda: None)
            self.__calibrate = self._read_calibration()
            self.__configs = self._read_configs()
            self.find_config()

            # Show battery when connecting
            self._show_battery()
        except NoCubeException:
            self.disconnect()
            raise
        except: 
            self.disconnect()
            raise

    def disconnect(self):
        self.__cache = defaultdict(lambda: None)
        
        """Disconnect the cube. Also stops the motor and shuts off the lights."""
        self.ser.write('bldcstop\n')
        self.ser.write('fbrgbled off tb 1 2 3 4 5 6\n')

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
        self.config = None

        command = self.__calibrate[action, direction]
        self.ser.write(command + '\n')

        self._timeout_fn = self.do_action
        self._timeout_args = [action, direction]
        t = threading.Timer(20.0, self._timeout_handler)
        t.start()
        while True:
            line = self.ser.readline()
            if 'Successfully' in line or 'Failed' in line:
                print line
                break
            elif 'complete' in line or 'failure' in line:
                print line
                break
        self.ser.flushInput()
        self.ser.flushOutput()
        t.cancel()

    def change_plane(self, alignment):
        """Change plane to align with a specified alignment.

        :param alignment: One of {(0, 0, 1), (1, 1, 0), (1, -1, 0)}
        """
        planes = [(0, 0, 1), (1, -1, 0), (1, 1, 0)]
        index = planes.index(alignment)
        
        def get_alignment():
            self.find_config()
            center = self.config['center']
            for i, a in enumerate(center):
                if a == 0:
                    return i, np.array(planes[i])
                elif a == 180:
                    return i, -np.array(planes[i])

        try_num = 0
        i, current = get_alignment()
        while True:
            if planes[i] == alignment:
                break
            if (i + 1) % 3 == index:
                self.do_action('change_plane', 'forward', sleep=10)
            else:
                self.do_action('change_plane', 'reverse', sleep=10)
            i, current = get_alignment()
        
        print('Final: {0} (tries: {1})'.format(self.config, try_num))

    def is_conected(self, face):
        # TODO: find better way to do this, as this does not always work
        light = self.read_light_sensor(face)                
        if light == 0:
            return True

    def send_message(self, face, message):
        self.ser.write('fbirled {0}\n'.format(face))
        self.ser.write('fbtxled {0} 1\n'.format(face))
        self.ser.write('fbtxcount {0}\n'.format(face))
        self.ser.write('fbtx {0} {1}\n'.format(face, message))
        self.ser.write('fbtxled {0}\n'.format(face))

    def read_message(self, face, length):
        self.ser.write('fbrxen {0} 1\n'.format(face))
        self.ser.write('fbrx {0} {1}\n'.format(face, length))

        self._timeout_fn = self.read_message
        self._timeout_args = [face, length]
        t = threading.Timer(5.0, self._timeout_handler)
        t.start()
        while True:
            line = self.ser.readline()
            if 'Read' in line:
                break
        msg = self.ser.readline()
        self.ser.flushInput()
        self.ser.flushOutput()
        t.cancel()
        
        return msg

    def read_mac_address(self):
        # Get MAC address of cube (unique)
        found = False
        line = ''

        # TODO: ensure callback semantics make sense
        def aux_fn(): print('Cannot re-execute read_mac_address')
            
        self._timeout_fn = aux_fn
        self._timeout_args = []
        t = threading.Timer(5.0, self._timeout_handler)
        t.start()
        while True:
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
        t.cancel()

        return line.split()[1]

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

        self._timeout_fn = self.read_imu
        self._timeout_args = [sensor]
        t = threading.Timer(5.0, self._timeout_handler)
        t.start()
        while True:
            line = self.ser.readline()
            if 'Gravity vector (int)' in line:
                break
        self.ser.flushInput()
        self.ser.flushOutput()
        s, e = line.index('['), line.index(']')
        gravity = [int(x) for x in line[s+1:e].split()]
        t.cancel()
        
        return gravity

    def read_light_sensor(self, face):
        """Read the light sensor at a face."""
        self.ser.write('fbrxen {0} 1\n'.format(face))
        self.ser.write('fblight {0}\n'.format(face))

        s = 'Faceboard {0} ambient light:'.format(face)

        self._timeout_fn = self.read_light_sensor
        self._timeout_args = [face]
        t = threading.Timer(5.0, self._timeout_handler)
        t.start()
        while True:
            line = self.ser.readline()
            if s in line:
                break
        self.ser.write('fbrxen {0} 0\n'.format(face))
        sensor = line.split(':')[1]
        try:
            val = int(sensor.strip())
        except ValueError:
            val = None
        
        self.ser.flushInput()
        self.ser.flushOutput()
        t.cancel()

        return val

    def read_light_sensors(self):
        """Reads the light sensors at each of the faces and returns a
        dictionary with results.
        """
        res = {}
        for face in xrange(1, 7):
            res[face] = self.read_light_sensor(face)

        result = {}
        for k, v in self.config.items():
            if k in ('top', 'bottom', 'left', 'right', 'forward', 'reverse'):
                result[k] = res[v]

        return result

    def find_config(self):
        if self.config:
            return
        
        readings = {}
        min_light = float('inf')
        for face in xrange(1, 7):
            readings[face] = self.read_light_sensor(face)
            if readings[face] is not None:
                min_light = min(min_light, readings[face])

        plane_c = self.find_angles('c')
        for config in self.__configs:
            dist_c = np.dot(plane_c - config['center'], plane_c - config['center'])
            bottom = config['bottom']
            if  dist_c < 10 and readings[bottom] == min_light:
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
    
    def _show_battery(self):
        self.ser.write('vbat\n')
        
        self._timeout_fn = self._show_battery
        self._timeout_args = []
        t = threading.Timer(5.0, self._timeout_handler)
        t.start()
        while True:
            line = self.ser.readline()
            if 'Battery' in line:
                break
        self.ser.flushInput()
        self.ser.flushOutput()
        t.cancel()
        
        battery = int(re.findall('\d+', line)[-1])
        if battery >= 3950:
            self.ser.write('fbrgbled g tb 1 2 3 4 5 6\n')
        elif battery >= 3600:
            self.ser.write('fbrgbled rg tb 1 2 3 4 5 6\n')
        else:
            self.ser.write('fbrgbled r tb 1 2 3 4 5 6\n')
        def stop_showing():
            time.sleep(3)
            self.ser.write('fbrgbled off tb 1 2 3 4 5 6\n')
        threading.Thread(target=stop_showing).start()

    def _timeout_handler(self):
        print('Timeout in {0}'.format(self._timeout_fn.__name__))
        print('Re-executing function {} with args {}'.format(self._timeout_fn.__name__, self._timeout_args))
        self._timeout_fn(*self._timeout_args)
