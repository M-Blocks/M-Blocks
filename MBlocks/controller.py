import csv
import operator
import re
import serial
import time
import urllib2


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

        self.mac_address = self._read_mac_address()

        self.reverse = False
        self.neighbours = []

        # Forward is the along the positive x-axis
        self.direction = [1, 0]

        self.__calibrate = self._read_calibration()
        self.__configs = self._read_configs()

    def disconnect(self):
        """Disconnect the cube."""
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
        config = self._find_config()
        if config['Left'] == face:
            self.change_plane('Left')
        elif config['Right'] == face:
            self.change_plane('Right')

        config = self._find_config()
        if config['Forward'] == face:
            self.do_action('traverse', 'forward')
        elif config['Backward'] == face:
            self.do_action('traverse', 'reverse')

    def do_action(self, action, direction):
        """Performs an action until it is successful."""
        command = self.__calibrate[action, direction]
        self.ser.write(command + '\n')
        time.sleep(5)

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

        :param direction: One of {Left, Right, Top, Bottom}.
        """
        forward = 'cp b f 4000 50\n'
        reverse = 'cp b r 4000 50\n'

        config = self._find_config()
        if direction is 'Top' or direction is 'Bottom':
            face = 0
        else:
            face = config[direction]

        try_num = 0
        while config['Forward'] != face and config['Backward'] != face:
            if config['Left'] == face:
                self.ser.write(forward)
            else:
                self.ser.write(reverse)
            time.sleep(15)
            config = self._find_config()
            if config is None:
                config = {'Forward': -1, 'Backward': -1, 'Left': face}

            try_num += 1

        print('Final: {0} (tries: {1})'.format(config, try_num))

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

    def find_strongest_light_signal(self):
        """Returns the face number and sensor value of the face with
        the strongest light stimulation.

        Excludes the Top and Bottom faces.
        """
        sensors = self._read_light_sensors()
        sensors = {k: v for k, v in sensors.items() if k not in ('Top', 'Bottom')}
        face, value = max(sensors.items(), key=operator.itemgetter(1))

        return face, value

    def light_follower(self):
        while True:
            face, _ = self.find_strongest_light_signal()
            move_towards(face)

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
                direction = row[2]
                for i in range(3, len(labels)):
                    result[labels[i], direction] = row[i].strip()

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

        result = {}
        config = self._find_config()
        for k, v in config.items():
            if k in ('Top', 'Bottom', 'Left', 'Right', 'Forward', 'Backward'):
                result[k] = res[v]

        return result

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
