from itertools import izip

import serial
import time

def connect(port, baud=115200):
    """Connect to a serial port at a given baud rate.

    :param port: Port number to connect to.
    :type port: str.
    :param baud: Baud rate (default 115200).
    :type baud: int.
    """
    ser = serial.Serial(port, baud, timeout=1)
    ser.write('atd\n')
    return ser

def disconnect(ser):
    """Disconnect a serial connection.

    :param ser: Serial connector to disconnect.
    :type ser: serial.Serial.
    """
    ser.write('blediscon\n')
    if ser.isOpen():
        ser.close()

def command(serials, commands, sleep_dur):
    """Send each serial in serials a sequence of commands.

    :param serials: List of serial connectors.
    :type serials: list of serial.Serial.
    :param commands: List of commands to execute sequentially.
    :type commands: list of str.
    :param sleep_dur: Time to sleep between consecutive commands.
    :type sleep_dur: list of int.
    """
    for c, t in izip(commands, sleep_dur):
        for ser in serials:
            if not ser.isOpen():
                ser.open()
            ser.write(c)
            ser.write('\n')
            ser.close()

        time.sleep(t)
