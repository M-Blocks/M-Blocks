#!/usr/bin/env python
from itertools import izip

import math
import serial
import time

import utils
import gui

# For the visualizer
import requests
import websocket
import shortuuid
import subprocess
import os
import threading

class Cube(object):
    def __init__(self, port, baud=115200, neighbors=None):
        """Connect to a serial port at a given baud rate.

        :param port: Port number to connect to.
        :type port: str.
        :param baud: Baud rate (default 115200).
        :type baud: int.
        :param neighbors: An object that defines the neighbors of a cube.
        :type neighbors: neighbor object.
        """

        # Initialize connection to cube
        if port is not None: 
            self.ser = serial.Serial(port, baud, timeout=1)
            self.ser.write('atd\n')
        # This allows for "headless" cube instances that do not have serial connections to physical cubes
        else:
            self.ser = None

        # Set instance variables
        # Make a 5 char serialNumber for the cube
        self.serialNumber = shortuuid.uuid()[:5] 
        self.orientation = 0
        self.reverse = False

        # This object keeps track of the cube's neighbors.
        if neighbors is None:
            self.neighbors = Neighbors()
        else: 
            # the list of neighbors came prepopulated on initialization. Make sure to use them.
            self.neighbors = neighbors

        self._left = {1: True, 2: False, -1: False, -2: True}
        self._right = {1: False, 2: True, -1: True, -2: False}

        # Forward is the along the positive x-axis
        self.direction = [1, 0]

        self.initializeVisualizer()

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

    def move(self, direction):
        """Move cube in specified direction.

        :param direction: One of {left, right, forward, backward, up,
            down}; case insensitive.
        """
        # TODO: Only moves it along the xy-plane

        forward = 'ia f 5000 2000 250\n'
        reverse = 'ia r 5000 1500 250\n'

        if direction not in ('forward', 'backward'):
            self.change_plane(direction)

        if self.reverse:
            forward, reverse = reverse, forward
        if direction is 'backward':
            forward, reverse = reverse, forward

        self.ser.write(forward)
        time.sleep(5)

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
                    self.move('forward')
                elif dirx != 0 and dirx != sgnx:
                    self.move('backward')
                elif dirx == 0:
                    self.change_plane('left')
                    state[0] -= sgnx

            elif dy != 0:
                state[1] += sgny
                print 'State: {0}'.format(state)
                if diry == sgny:
                    self.move('forward')
                elif diry != 0 and diry != sgny:
                    self.move('backward')
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
            self.move(direction)
            state = update(state, direction)

    def gui(self):
        root = Tk()

        app = App(root, self)

        root.mainloop()
        root.destroy()

    def restartVisualizerDaemon(self):
        print "Visualizer supervisor unreacheable. Restarting visualizer."

        # Try to restart the visualizer process
        sourceDir = os.path.dirname(os.path.realpath(__file__))
        visualizerDir = os.path.join(sourceDir, 'cube_map_visualizer')

        # cd into visualizer dir
        os.chdir(visualizerDir)

        visualizerPath = os.path.join(visualizerDir, 'make_dist.sh')
        print visualizerPath
        subprocess.Popen([visualizerPath])

        time.sleep(5)

    # This function initiates a connection to the visualizer supervisor process. 
    def initializeVisualizer(self):
        # Try to make a connection to the visualizer process. 

        def on_message(ws, message):
            #print message
            pass

        def on_error(ws, error):
            print error

        def on_close(ws):
            print "### websocket closed ###"

        try:
            onlineCheck = request.get('http://localhost/:8000')
            onlineCheck.raise_for_status()

            self.ws = websocket.WebSocketApp("ws://localhost/:8000",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close)
        
        except:
            self.restartVisualizerDaemon()
            self.initializeVisualizer()
        
        # Now, start updating the visualizer every second.
        self.updateVisualizer()


    # This function is called once every second and updates the visualizer with the current cube's orientation, serial number, and neighbor locations.
    def updateVisualizer(self):

        cube_status = {
        'serialNumber': self.serialNumber,
        'orientation': self.orientation,
        'neighbors': self.neighbors
        }

        # Send HTTP PUT request to visualizer
        try:
            self.ws.send(cube_status)

        except:
            # If the visualizer did not update correctly
            print 'Cube visualizer update failed. Check that the visualizer backend is running.'

        # Set this function to run every second
        threading.Timer(1.0, self.updateVisualizer)

# This object is used once by each cube class to keep track of its neighboring cubes
class Neighbors(object):
    def __init__(self):
        self.neighbors = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}

    # This method sets/overrides the neighbor registration at a certain face. Orientation is in degrees I.E(0, 90, 180, 270).
    def setNeighbor(self, face, serialNumber, orientation):

        self.neighbors[face] = {
            'serialNumber': serialNumber,
            'orientation': orientation
        }

    # Get the python dictionary that represents this cube's neighbors
    def getNeighbors(self):
        return self.neighbors



# Main loop for running program via command line
if __name__ == "__main__":
    # Create a cube object with a neighbor on face 1
    cube1 = Cube(port=None)
    cube1.neighbors.setNeighbor(1, 'cube2', 0)

    # Create a second cube object with no neighbors
    lonelyCube = Cube(port=None)

    # Create a third cube object with cube1 as a neighbor on face 3

    cube2 = Cube(port=None)
    cube2.neighbors.setNeighbor(3, 'cube1', 0)


