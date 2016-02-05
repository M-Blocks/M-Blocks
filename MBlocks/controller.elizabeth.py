import serial.tools.list_ports
from difflib import SequenceMatcher
import csv
import math
import operator
import re
import serial
import time
import threading
import urllib2
import operator
import numpy as np

##import MBlocks.utils as utils
import utils

global globi;

global remainingCubes;


class NoCubeException(Exception):
    pass
getComp = {1:3,3:1,2:4,4:2,6:5,5:6} ##opposite side of the cube
##right hand rule given xz returns y
rhr = {'14':6,'16':2,'12':5,'15':4,'23':5,'26':3,'21':6,'25':1,'36':4,'32':6,'35':2,'34':5,'41':5,'46':1,'43':6,'45':3,'51':2,'54':1,'53':4,'52':3,'61':4,'62':1,'63':2,'64':3}
##right hand rule given xy returns -z i think
rhrnorm = {'12':6,'16':4,'14':5,'15':2,'21':5,'25':3,'23':6,'26':1,'32':5,'35':4,'34':6,'36':2,'41':6,'46':3,'43':5,'45':1,'51':4,'54':3,'53':2,'52':1,'61':2,'62':3,'63':4,'64':1}
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
        self.centerLoc = 'undef'

        self.faceUp = 10
        self.faceDown = 10
        self.lastLightReadings = {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1}
        self.neighbors = {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1}
        self.facesDir = [0,0,0,0,0,0,0]
        self.darkFaces = []

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
        ##what does the variable sensor do?
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


def discon(lMacAdr): ##disconnect cubes
    if lMacAdr:
        for cube in listOfCubes:
            for macAdr in lMacAdr:
                if cube.mac_address == macAdr:
                    cube.disconnect()
    if not lMacAdr:
        for cube in listOfCubes:
            cube.disconnect()

def all_red(): ##light up red all connected cubes
    for cube in listOfCubes:
        cube.ser.write('fbrgbled r tb 1 2 3 4 5 6\n')

def all_mac_adr():
    for cube in listOfCubes:
        print cube.mac_address

def ir_off():
   for cube in listOfCubes:
            cube.ser.write('fbirled 1\n')
            cube.ser.write('fbirled 2\n')
            cube.ser.write('fbirled 3\n')
            cube.ser.write('fbirled 4\n')
            cube.ser.write('fbirled 5\n')
            cube.ser.write('fbirled 6\n') 
        
def command(command,lMacAdr):
    if lMacAdr:
        for cube in listOfCubes:
            for macAdr in lMacAdr:
                if cube.mac_address == macAdr:
                    cube.ser.write(command)
    if not lMacAdr:
        for cube in listOfCubes:
            cube.ser.write(command)

def lightOnFaces(lMacAdr):
    if lMacAdr:
        for cube in listOfCubes:
            for macAdr in lMacAdr:
                if cube.mac_address == macAdr:
                    cube.ser.write('fbrxen 0 1')
                    print "all: "+ str(cube._read_light_sensors())
                    stats = cube._read_light_sensors()
                    cube.lastLightReadings = stats
                    cube.darkFaces = []
                    for face, val in stats.items():
                        if val == 0:
                            cube.darkFaces.append(face)
                    print "dark faces: "+ str(cube.darkFaces)
                    cube.faceUp = max(stats.iteritems(), key=operator.itemgetter(1))[0]
                    print "side up: " +str(cube.faceUp)
                    cube.ser.write('fbrxen 0 0')
                    
    if not lMacAdr:
        for cube in listOfCubes:
            cube.ser.write('fbrxen 0 1')
            print "all: "+ str(cube._read_light_sensors())
            stats = cube._read_light_sensors()
            cube.lastLightReadings = stats
            cube.darkFaces = []
            for face, val in stats.items():
                if val == 0:
                    cube.darkFaces.append(face)
            print "dark faces: "+ str(cube.darkFaces)
            cube.faceUp = max(stats.iteritems(), key=operator.itemgetter(1))[0]
            print "side up: " +str(cube.faceUp)
            cube.ser.write('fbrxen 0 0')

def find_connections (lMacAdr):
    ir_off()
    lightOnFaces([])
    if lMacAdr:
        print "derp derp write some code"
    if not lMacAdr:
        posConnectCubes = []
        for cube in listOfCubes:
            cube.neighbors = {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1}
            if len(cube.darkFaces) >1:
                posConnectCubes.append(cube)
        for cube in posConnectCubes:
            print cube.mac_address
            for face in cube.darkFaces:
                cube.ser.write('fbirled ' +str(face)+' 1 2 3 4\n')
                for otherCube in posConnectCubes:
                    cube.ser.write('fbrxen 0 1')
                    if cube !=otherCube:
                        for faceOther in otherCube.darkFaces:
                            print str(faceOther) + "and" + str(face)+ "val "+ str(otherCube._read_light_sensor(faceOther))
                            if otherCube._read_light_sensor(faceOther) > 5:
                                cube.neighbors[str(face)+str(faceOther)] = otherCube;
                                otherCube.neighbors[str(faceOther)+str(face)] = cube;
                                print otherCube._read_light_sensor(faceOther)
                                print str(faceOther) + "and" + str(face) +"are connected!"       
                    cube.ser.write('fbrxen 0 0')
                cube.ser.write('fbirled ' +str(face)+'\n')
                ir_off()
                print "ir off"
    ir_off()
        
    

def locateCubes():
    j=0
    global remainingCubes
    remainingCubes = set(listOfCubes)
    for cube in listOfCubes:
        cube.facesDir = [0,0,0,0,0,0,0]
    if (j==0):
        cube = remainingCubes.pop()
        locateCube1(cube)
        j=1
        print "try 1" + str(cube.mac_address)
        for key in cube.neighbors:
            print "try 2" + str(cube.mac_address)
            if cube.neighbors[key] in remainingCubes:
                print "try 3" + str(cube.mac_address)
                locateCube(cube, key)
    else:
        print "code not yet written"
        

def locateCube(oldCube, key):
    global remainingCubes
    
    cube = oldCube.neighbors[key]
    print "oldCube" +str(oldCube.mac_address)
    print "cube"+str(cube.mac_address)
    print key
    oldCubeFace = int(key[0])
    print oldCubeFace
    cubeFace = int(key[1])
    print cubeFace
    print oldCube.centerLoc
    print oldCube.facesDir[oldCubeFace]
    ##print np.asarray(oldCube.centerLoc)+np.asarray
    cube.centerLoc = list(np.asarray(oldCube.centerLoc) + np.asarray(oldCube.facesDir[oldCubeFace]))
    print "try 1" + str(cube.facesDir)
    cube.facesDir[cubeFace] = list(-1*np.asarray(oldCube.facesDir[oldCubeFace]))
    cube.facesDir[int(getComp[cubeFace])] = oldCube.facesDir[oldCubeFace]
    print "try 2" + str(cube.facesDir)
    cube.facesDir[cube.faceUp]=[0,0,1]
    cube.facesDir[int(getComp[cube.faceUp])]=[0,0,-1]
    
    print "trying here" + str(cube.facesDir)
    temp=-1
    for direction in cube.facesDir:
        print direction
        temp = temp + 1
        if direction == [0,1,0]:
            print "in if"
            face90 = str(rhrnorm[str(temp)+str(cube.faceUp)])
            cube.facesDir[int(face90)] = [1,0,0]
            cube.facesDir[int(getComp[int(face90)])] = [-1,0,0]
            break
        elif direction == [1,0,0]:
            print "in else"
            face90 = str(rhr[str(temp)+str(cube.faceUp)])
            cube.facesDir[int(face90)]=[0,1,0]
            cube.facesDir[int(getComp[int(face90)])]=[0,-1,0]
            break
            
    print "RESULT2: face up: "+str(cube.faceUp)+" center: "+str(cube.centerLoc)+" faces: "+str(cube.facesDir)
 

    for key in cube.neighbors:
                if cube.neighbors[key] in remainingCubes:
                    locateCube(cube, key)
    
    
    
def locateCube1(cube1):
    faceDown = getComp[cube1.faceUp];
    cube1.facesDir[faceDown] = [0,0,-1]
    cube1.facesDir[cube1.faceUp]=[0,0,1]
    print "FaceDown is " + str(faceDown) + "faceUp is " + str(cube1.faceUp)
    print (faceDown == 2)
    if ((faceDown != 1) and (faceDown != 3)):
        print "in if"
        cube1.facesDir[1] = [1,0,0]
        cube1.facesDir[3]=[-1,0,0]
        face90 = rhr[str(1)+str(getComp[faceDown])]
        cube1.facesDir[int(face90)]=[0,1,0]
        cube1.facesDir[int(getComp[int(face90)])]=[0,-1,0]
			
    elif faceDown != (2 or 4):
        print "in elif"
        cube1.facesDir[2] =[1,0,0]
        cube1.facesDir[4] = [-1,0,0]
        face90 = rhr[str(2)+str(getComp[faceDown])]
        cube1.facesDir[int(face90)]=[0,1,0]
        cube1.facesDir[int(getComp[int(face90)])] = [0,-1,0]
                              
    cube1.centerLoc = [0,0,0]
    print "RESULT: face up: "+str(cube1.faceUp)+" center: "+str(cube1.centerLoc)+" faces: "+str(cube1.facesDir)

    
    
    
def add_cubes():
    global globi
    listPorts = []
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        strP = str(p)
        m = SequenceMatcher(None,strP, "COM - Bluegiga Bluetooth Low Energy (COM)")
        if (m.ratio() > 0.90):
            part1 = strP.split(' ')[0]
            listPorts.append(part1)
    print listPorts
    listAvailablePorts = [x for x in listPorts if x not in listUsedPorts]
    print listUsedPorts
    for port in listAvailablePorts:
        print "about to try" + str(globi)    
        try:
            print listPorts[globi]
            cube = Cube(listPorts[globi])
            listOfCubes.append(cube);
            listUsedPorts.append(listPorts[globi]);
            print "my mac address is " + str(cube.mac_address)
            globi=globi+1
        except NoCubeException:
            print "no more cubes available"

##on start of prog checks which computer ports are connected to bluetooth devices    
listPorts = []
ports = list(serial.tools.list_ports.comports())
for p in ports:
    strP = str(p)
    m = SequenceMatcher(None,strP, "COM - Bluegiga Bluetooth Low Energy (COM)")
    if (m.ratio() > 0.90):
        part1 = strP.split(' ')[0]
        listPorts.append(part1)
print listPorts

##then connects to as many cubes as it can
listUsedPorts = [];
listOfCubes = [];
listAvailablePorts = [x for x in listPorts if x not in listUsedPorts]
global globi;
globi = 0;
for port in listAvailablePorts:
    print "about to try" + str(globi)    
    try:
        print listPorts[globi]
        cube = Cube(listPorts[globi])
        listOfCubes.append(cube);
        listUsedPorts.append(listPorts[globi]);
        print "my mac address is " + str(cube.mac_address)
        ##print "cube " + str(globi) + " has orientation" +str(cube.get_orientation())
        globi=globi+1
    except NoCubeException:
        print "no more cubes available"
listAvailablePorts = [x for x in listPorts if x not in listUsedPorts]





