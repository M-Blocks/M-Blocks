'''
Created on 2011-12-02

@author: Bobby Wood
'''


## import the serial library
import serial
import time
import sys
import Tkinter
import tkMessageBox
from Tkinter import *


def sendMes (mess, block):
    ##self.ser = serial.Serial(comDev, 115200, timeout=2)

    ## Boolean variable that will represent 
    ## whether or not the arduino is connected
    connected = False

    ## open the serial port that your ardiono 
    ## is connected to.
    ser = serial.Serial("COM8", 9600, timeout =10)
    ##ser.write("1")

    ## loop until the arduino tells us it is ready
    while not connected:
        serin = ser.read()
        ##print ser.read()
        ##print(serin)
        connected = True
        
    startTime = time.time();
    ## Tell the arduino to blink!
    ##text = "0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz0123456????????????????????????????????????????????????"
    text = "sendcmd;" + block + ";" + mess + "|";
    print text
    length = len(text);
    if length> 79:
        print "input too long";
    newText = "";
    for i in range (0,127):
        if (i<79):
            if i<length:
                newText += text[i];
            else:
                newText += "?";
        elif (i==126 or i==127):
            newText += "|";
        else:
            newText += "?"
    ##newText = "sendcmd;a;fbrgbled g tb 4 2|";
    ##text = str(len(text))+text
    print newText
    ser.write(newText)
    ser.flush()
    ##time.sleep(5)
        

    ## Wait until the arduino tells us it 
    ## is finished blinking
    ## while ser.read() == '1':
    ##    continue

    while(time.time() - startTime <3):
        ##sys.stdout.write(ser.read())
        h=0;

    ser.close()

    ## close the port and end the program
    ##print ser.read(800)
    ##ser.close()
    print "all done"


top = Tkinter.Tk()


def greenLED():
    sendMes('fbrgbled g tb 1 2 3 4', 'a')

def redLED():
    sendMes('fbrgbled r tb 1 2 3 4', 'a')

def blueLED():
    sendMes('fbrgbled b tb 1 2 3 4', 'a')
    
def plane():
    sendMes('cp b f 5000 40','a')

def offLED():
    sendMes('fbrgbled off tb 1 2 3 4', 'a')

def readInput():
    stringcmd = E1.get()
    for char in stringcmd:
        if char == "g" or char == "G":
            sendMes('fbrgbled g tb 1 2 3 4', 'a')
        if char == "r" or char == "R":
            sendMes('fbrgbled r tb 1 2 3 4', 'a')
        if char == "b" or char == "B":
            sendMes('fbrgbled b tb 1 2 3 4', 'a')
        if char == "p" or char == "P":
            sendMes('cp b f 5000 40', 'a')
        if char == "o" or char == "O":
            sendMes('fbrgbled off tb 1 2 3 4', 'a')
    E1.delete('0', END)

B = Tkinter.Button(top, text ="Green", command = greenLED)
C = Tkinter.Button(top, text ="Red", command = redLED)
D = Tkinter.Button(top, text ="Blue", command = blueLED)
G = Tkinter.Button(top, text ="change plane", command = plane)
E = Tkinter.Button(top, text ="Off", command = offLED)
F = Tkinter.Button(top, text ="ReadText", command = readInput)

L1 = Label(top, text="Series of colors")

E1 = Entry(top, bd =5)



B.pack()
C.pack()
D.pack()
G.pack()
E.pack()
F.pack()
##L1.pack()
E1.pack()
top.mainloop()

##text = "sendcmd;a;fbrgbled off tb 4 2|";

