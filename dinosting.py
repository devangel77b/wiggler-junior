#!/usr/bin/env python

# Module:   dinosting.py
# Created:  10 November 2010
# Author:   Dennis Evangelista
# Version:  0.1
# License:  GPLv3

'''
This module provides a serial connection abstraction layer for talking to
the wind tunnel and sting for 4115 VLSB Microraptor gui experiments in
the Department of Integrative Biology, UC Berkeley.
'''

import serial
from serial.serialutil import SerialException

class DinoSting:
    '''class DinoSting is an instance of a wind tunnel and sting.'''

    # Static attributes for talking to Arduino.
    # Must match definitions in DinoStingFan.pdf Arduino code.
    START = chr(255) # Start byte code
    SERVO = chr(1)   # Servo byte code
    FAN = chr(2)     # Fan byte code

    def __init__(self,port='COM4',mount_angle=0):
        ''' DinoSting constructor takes port (default COM4) and mount angle.'''
        self.mount_angle = mount_angle
        try:
            self.ser = serial.Serial(port, timeout = 1)
            print 'Connected on {0}.'.format(port)
        except SerialException:
            print 'Could not connect with Arduino on {0}, is it plugged in?'.format(port)
        # other possibilities are
        # port = '/dev/tty.usbserial-A600ehci' for mac
        # port = '/dev/ttyUSB0' for linux



    def move(self,angle=0):
        '''Moves the servo sting to the supplied angle.  Angle must be
between 0 and 180 degrees.'''
        if (0 <= (angle-self.mount_angle) <= 180):
            self.ser.write(DinoSting.START)
            self.ser.write(DinoSting.SERVO)
            self.ser.write(chr(angle-self.mount_angle))
            print 'Sting trained to %d adjusted or %d raw.' % (angle,(angle-self.mount_angle))
        else:
            print 'Servo angle plus mount angle must be an integer between 0 and 180.'



    def fan(self,state=0):
        '''Changes the speed of the fan'''
        
        if (state != 0):
            print 'Fan running at %d/255 of maximum speed.' % (state)
            self.ser.write(DinoSting.START)
            self.ser.write(DinoSting.FAN)
            self.ser.write(chr(state))
        else:
            print 'Fan secured.'
            self.ser.write(DinoSting.START)
            self.ser.write(DinoSting.FAN)
            self.ser.write(chr(state))


    def gohome(self):
        print 'Going home...'
        self.move(0)
        self.fan(0)
        print 'Wind tunnel home.'
        


    def shutdown(self):
        ''' Zeros servo position and turns off fan'''
        print 'Shutting down...'
        self.move(0)
        self.fan(0)
        print 'Wind tunnel secured.'




    def __del__(self):
        ''' DinoSting destructor shuts down port and secures serial port.'''
        self.shutdown()
        self.ser.close()
        print 'DinoSting object garbage collected.'
        
 
        

        
