import serial

ports = input('Enter ports to disconnect (separated by spaces -- e.g. \'com6 com7 com8\'): ').split()
for port in ports:
    ser = serial.Serial(port, baudrate=115200)
    ser.write('blediscon\n')
    ser.close()
