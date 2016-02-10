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

import MBlocks.utils as utils
import numpy as np

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

        try:
            self.mac_address = self._read_mac_address()

            self.reverse = False
            self.neighbours = []

            # Forward is the along the positive x-axis
            self.direction = [1, 0]

            self.__calibrate = self._read_calibration()
            self.__configs = self._read_configs()
            self._find_config()

            # Show battery when connecting
            self._show_battery()
        except NoCubeException:
            raise
        except: 
            e = sys.exc_info()[0]
            print e
            if self.ser.isOpen():
                self.ser.write('bldcstop\n')
                self.ser.write('fbrgbled off tb 1 2 3 4 5 6\n')
                self.ser.write('blediscon\n')
                self.ser.close()
            raise

    def disconnect(self):
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

        mac_address = self._read_mac_address()
        while mac_address != self.mac_address:
            time.sleep(5)
            self.ser.write('blediscon\n')
            time.sleep(2)
            self.ser.write('atd\n')
            time.sleep(5)
            mac_address = self._read_mac_address()

    def move_towards(self, face):
        print 'Moving towards {0}: '.format(face)
        if face == 'Forward':
            self.do_action('traverse', 'forward')
        elif face == 'Backward':
            self.do_action('traverse', 'reverse')
        time.sleep(6)
        self._find_config()

    def do_action(self, action, direction):
        """Performs an action until it is successful."""
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
            after = self._find_config()

    def change_plane(self, alignment):
        """Change plane to align with a specified alignment.

        :param alignment: One of {(0, 0, 1), (1, 1, 0), (1, -1, 0)}
        """
        forward = self.__calibrate['change_plane', 'forward']

        try_num = 0
        while self.config['Central Alignment'] != alignment and self.config['Central Alignment'] != (-alignment):
            self.ser.write(forward)
            time.sleep(10)
            self._find_config()

            try_num += 1

        print('Final: {0} (tries: {1})'.format(self.config, try_num))

    def send_message(self, face, message):
        self.ser.write('fbirled {0}\n'.format(face))
        self.ser.write('fbtxled {0} 1\n'.format(face))
        self.ser.write('fbtxcount {0}\n'.format(face))
        self.ser.write('fbtx {0} {1}\n'.format(face, message))
        self.ser.write('fbtxled {0}\n'.format(face))

    def read_message(self, face, length):
        self.ser.write('fbrxen {0} 1\n'.format(face))
        self.ser.write('fbrx {0} {1}\n'.format(face, length))

        while True:
            line = self.ser.readline()
            if 'Read' in line:
                break
        msg = self.ser.readline()
        return msg

    def bdcastcmd(self, command):
        self.ser.write('fbirled 0\n')
        self.ser.write('fbtxled 0\n')

        # TODO
        m, t = string.lower('1'), int(time.time())
        message = 'bdcastcmd;{0}+{1};{2}'.format(m, t, command)
        self.ser.write('fbtx 0 {0}\n'.format(message))

    def sendcmd(self, dest, command):
        self.ser.write('fbirled 0\n')
        self.ser.write('fbtxled 0\n')

        # TODO
        m, t = string.lower('1'), int(time.time())
        message = 'sendcmd;{0}+{1};{2};{3}'.format(m, t, dest, command)
        self.ser.write('fbtx 0 {0}\n'.format(message))

    def find_strongest_light_signal(self):
        """Returns the face number and sensor value of the face with
        the strongest light stimulation.

        Excludes the Top and Bottom faces.
        """
        sensors = self._read_light_sensors()
        #sensors = {k: v for k, v in sensors.items() if k not in ('Top', 'Bottom')}
        face, value = max(sensors.items(), key=operator.itemgetter(1))

        return face, value

    def light_follower(self, thresh, ratio):
        sensors = self._read_light_sensors()
        bottom_value = sensors['Bottom']
        non_zero = {k: v for k, v in sensors.items() if v is not None and v > bottom_value and k != 'Top'}
        print non_zero

        # assume we are not connected to another cube
        if min(non_zero.items()) < 10:
            return None, None

        vals = non_zero.values()
        max_value = max(non_zero.values())
        min_value = min(non_zero.values())
        if float(min_value) / float(max_value) > ratio or max_value < thresh:
            return None, None
        else:
            return max(non_zero.keys(), key=lambda x: non_zero[x]), max_value

    def _show_battery(self):
        self.ser.write('vbat\n')
        while True:
            line = self.ser.readline()
            if 'Battery' in line:
                break

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

    def _read_mac_address(self):
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

        self.ser.flushInput()
        self.ser.flushOutput()

        return line.split()[1]

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
                direction = row[5].strip()
                for i in range(6, len(labels)):
                    result[labels[i].strip(), direction] = row[i].strip()

        return result

    def _read_imu(self, sensor):
        self.ser.write('imuselect {0}\n'.format(sensor))
        self.ser.write('imugravity\n')
        while True:
            line = self.ser.readline()
            if 'Gravity vector (int)' in line:
                break
        s, e = line.index('['), line.index(']')
        gravity = [int(x) for x in line[s+1:e].split()]
        
        thresh = 10
        planes = np.array([(0, 0, 1), (1, -1, 0), (1, 1, 0)])

        for i, plane in enumerate(planes):
            angle = utils.angle(plane, gravity) / math.pi * 180
            if angle < thresh:
                return plane
            elif angle > 180 - thresh:
                return -plane

        return None

    def _read_light_sensor(self, face):
        """Read the light sensor at a face."""
        self.ser.write('fbrxen {0} 1\n'.format(face))
        self.ser.write('fblight {0}\n'.format(face))

        s = 'Faceboard {0} ambient light:'.format(face)
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

        return val

    def _read_light_sensors(self):
        """Reads the light sensors at each of the faces and returns a
        dictionary with results.
        """
        res = {}
        for face in xrange(1, 7):
            res[face] = self._read_light_sensor(face)

        result = {}
        for k, v in self.config.items():
            if k in ('Top', 'Bottom', 'Left', 'Right', 'Forward', 'Backward'):
                result[k] = res[v]

        return result

    def _find_config(self):
        readings = {}
        min_light = float('inf')
        for face in xrange(1, 7):
            readings[face] = self._read_light_sensor(face)
            if readings[face] is not None:
                min_light = min(min_light, readings[face])

        central_plane = self._read_imu('c')
        central_label = 'Central Alignment'
        for config in self.__configs:
            bottom = config['Bottom']
            if np.array_equal(config[central_label], central_plane) and readings[bottom] == min_light:
                self.config = config
                break
