import csv
import math
import operator
import re
import serial
import time
import threading
import urllib2

import MBlocks.utils as utils


class NoCubeException(Exception):
    pass


class Cube(object):
    def __init__(self, port, baud=115200, position=(0, 0, 0)):
        """Connect to a serial port at a given baud rate.

        :param port: Port number to connect to.
        :type port: str.
        :param baud: Baud rate (default 115200).
        :type baud: int.
        """
        self.ser = serial.Serial(port, baud, timeout=1)
        self.ser.write('atd\n')

        self.mac_address = self._read_mac_address()

        self.reverse = False
        self.neighbours = []

        # Forward is the along the negative x-axis
        self._left = {1: True, 2: False, -1: False, -2: True}
        self._right = {1: False, 2: True, -1: True, -2: False}

        # Forward is the along the positive x-axis
        self.direction = (1, 0, 0)
        self.position = position

        self.__calibrate = self._read_calibration()

        # Show battery when connecting
        self._show_battery()

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

    def do_action(self, action, direction):
        """Performs an action until it is successful."""
        command = self.__calibrate[action, direction]
        self.ser.write(command + '\n')
        time.sleep(5)

    def get_orientation(self):
        self.ser.write('imugravity\n')

        line = ''
        while True:
            try:
                line = self.ser.readline()
                if 'Gravity vector (int)' in line and '[' in line and ']' in line:
                    break
            except serial.serialutil.SerialException:
                pass

        s, e = line.index('['), line.index(']')
        grav = [int(x) for x in line[s+1:e].split()]

        thresh = 10
        planes = [(0, 0, 1), (1, -1, 0), (1, 1, 0)]

        print grav
        for i, plane in enumerate(planes):
            angle = utils.angle(plane, grav) / math.pi * 180
            if angle < thresh:
                return plane
            elif angle > 180 - thresh:
                return -plane

    def change_plane(self, old_plane, new_plane):
        while new_plane != old_plane:
            self.ser.write('cp b f 5000 50\n')
            line = ''
            while True:
                try:
                    line = self.ser.readline()
                    if 'Failed to change planes' in line or 'Successfully changed planes' in line:
                        break
                except serial.serialutil.SerialException:
                    pass
            time.sleep(1)
            old_plane = self.get_orientation()
            print old_plane

    def change_rotation_axis(self, new_axis):
        if new_axis == self.rotation_axis:
            return

        # All axes rotate counterclockwise when moving forward
        if sum(new_axis) < 0:
            new_axis = (-x for x in new_axis)
        plane = self.get_orientation()
        if new_axis == (0, 1, 0):
            new_plane = (0, 0, 1)
        else:
            if plane == (1, -1, 0):
                new_plane = (1, 1, 0)
            else:
                new_plane = (1, -1, 0)

        self.change_plane(plane, new_plane)

    def _show_battery(self):
        self.ser.write('vbat\n')
        while True:
            line = self.ser.readline()
            if 'Battery' in line:
                break

        battery = int(re.findall('\d+', line)[-1])
        if battery >= 3950:
            self.ser.write('fbrgbled g tb 1 2 3 4 5 6\n')
        elif battery >= 3800:
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
                direction = row[3].strip()
                for i in range(4, len(labels)):
                    result[labels[i].strip(), direction] = row[i].strip()

        return result

    def _read_imu(self, sensor):
        while True:
            try:
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
                break
            except IndexError:
                self.restart()

        return alpha, beta, gamma

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

        return res

    # def receiving(ser):
    #     buffer_string = ''
    #     while True:
    #         buffer_string += ser.read(ser.inWaiting())
    #         if '\n' in buffer_string:
    #             data = buffer_string.split('\n')[:-1]
    #             buffer_string = buffer_string.split('\n')[-1]

    #             for line in data:
    #                 if 'Gravity' in line:
    #                     s, e = line.index('['), line.index(']')
    #                     self.data['gravity'] = [float(x) for x in line[s+1:e].split()]
    #                     self.stale['gravity'] = False
    #                 if 'Angle between gravity vector' in line:
    #                     self.data['imu_angles'].append()
