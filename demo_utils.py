from MBlocks.control.controller import Cube
from MBlocks.planning.random_follower import RandomLightPlanner
from MBlocks.planning.light_follower import LatticeLightPlanner

from serial.tools.list_ports import comports
from serial import Serial

macs = ['d89c0041e41', 'fb0d8f2c3bb4', 'e6f6056908f2', 'cd2b5eab3ef3', 'df1ce4239c6e']

def ports():
    ps = [c[0] for c in comports()]
    return ps

def stop_fn_lattice(cube):
    connections = [cube.is_connected(face, 0) for face in range(1, 7)]
    connections = [c for c in connections if c]
    return len(connections) >= 2

def close_conns():
    for port in ports():
        ser = Serial(port)
        ser.write('blediscon\n')
        ser.close()

def shake_cubes(cubes):
    for cube in cubes:
        cube.ser.write('ia f 3500 2500 10\n')

def find_cubes():
    cubes = []
    for port in ports():
        try:
            cube = Cube(port)
            cubes.append(cube)
        except:
            pass
    return cubes