from itertools import izip

import math
import serial
import sys
import threading
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

        self.orientation = 0
        self.reverse = False

        self.neighbours = []

    def disconnect(self):
        """Disconnect a serial connection.

        :param ser: Serial connector to disconnect.
        :type ser: serial.Serial.
        """
        if not self.ser.isOpen():
            self.ser.open()
        self.ser.write('blediscon\n')
        self.ser.close()

    def command(self, commands, sleep_dur):
        """Send each serial in serials a sequence of commands.

        :param serials: List of serial connectors.
        :type serials: list of serial.Serial.
        :param commands: List of commands to execute sequentially.
        :type commands: list of str.
        :param sleep_dur: Time to sleep between consecutive commands.
        :type sleep_dur: list of int.
        """
        for c, t in izip(commands, sleep_dur + [0]):
            if not self.ser.isOpen():
                self.ser.open()
            self.ser.write(c)
            self.ser.write('\n')
            self.ser.close()

            time.sleep(t)

    def plan(self, state, goal, stimulus):
        """Plan a trajectory for the robot to move from the current
        state to the goal under a given stimulus function.

        Example: move from the current position towards a light source
        until the light stimulus is over a threshold (the goal).

        :param state: Current state of the robot.
        :param goal: Goal state of the robot.
        :param stimulus: Stimulus function that gives an updated state
            after the robot moves.
        """
        pass

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
                self.reverse = False
                break
            elif angle > 180 - thresh:
                self.orientation = i
                self.reverse = True
                break

        print 'Orientation: {0}'.format(self.orientation)
        print 'Reversed: {0}'.format(self.reverse)
