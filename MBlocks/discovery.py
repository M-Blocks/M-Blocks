from serial import tools
from serial.tools import list_ports

from controller import *

used = set()

def discovery():
    while True:
        ports = [port[0] for port in serial.tools.list_ports.comports() if 'ACM' in port[0]]
        for port in ports:
            if port in used:
                continue

            try:
                cube = Cube(port)
                acquire(port)
                yield cube
            except serial.SerialException:
                print 'Port {0} is not available'.format(port)
            except NoCubeException:
                print 'There is no cube on port {0}'.format(port)

def acquire(port):
    """Acquire hold on port.
    """
    used.add(port)

def release(port):
    """Release hold on port.

    Note that this must be called after a cube is disconnected.
    """
    used.remove(port)
