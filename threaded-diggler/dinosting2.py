#!/usr/bin/env python

# Module:   dinosting2.py
# Created:  10 November 2010
# Revised:  28 March 2012
# Author:   Dennis Evangelista
# Version:  0.2
# License:  GPLv3

'''
This module provides a serial connection abstraction layer for talking to
the wind tunnel and sting for 4115 VLSB Microraptor gui experiments in
the Department of Integrative Biology, UC Berkeley.
'''

import serial
import logging
import time

# Mercurial keywords disabled in Windoze7
HGAUTHOR = '$Author$: devangel'.split()[1]
HGREVISION = '$Revision$: blah'.split()[1]
HGDATE = '$Date$: today'.split()[1]


class DinoSting():
    '''class DinoSting is an instance of a wind tunnel and sting.'''

    # Static attributes for talking to Arduino.
    # Must match definitions in DinoStingFan.pdf Arduino code.
    START = chr(255) # Start byte code
    SERVO = chr(1)   # Servo byte code
    FAN = chr(2)     # Fan byte code
    RESET = chr(3)   # Arduino reset code / shuts down fan

    def __init__(self,port='COM3',mount_angle=0):
        ''' DinoSting constructor takes port (default COM3) and mount angle.'''
        self.mount_angle = mount_angle
        try:
            self.ser = serial.Serial(port, timeout = 1)
            logging.debug("Arduino connected on {0}.".format(port))
        except serial. SerialException:
            logging.critical("Could not connect with Arduino on {0}, is it plugged in?".format(port))
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
            logging.debug("Sting trained to %d adjusted or %d raw.".format(angle,(angle-self.mount_angle)))
        else:
            logging.critical("Servo angle plus mount angle must be an integer between 0 and 180.")



    def fan(self,state=0):
        '''Changes the speed of the fan'''
        
        if (state != 0):
            logging.debug("Fan running at {0}/255 of maximum speed.".format(state))
            fanSpeed = chr(state)
            self.ser.write(DinoSting.START)
            self.ser.write(DinoSting.FAN)
            self.ser.write(fanSpeed)
        else:
            logging.debug("Fan secured")
            self.ser.write(DinoSting.START)
            self.ser.write(DinoSting.FAN)
            self.ser.write(chr(0))


    def gohome(self):
        logging.debug("Sting going to home position, tunnel stopping")
        self.move(0)
        self.fan(0)


    def shutdown(self):
        ''' Zeros servo position and turns off fan'''
        logging.debug("Sting going to home position, tunnel stopping")
        self.move(0)
        self.fan(0)


    def __del__(self):
        ''' DinoSting destructor shuts down port and secures serial port.'''
        self.shutdown()
        self.ser.close()
        logging.debug("DinoSting object garbage collected")

        
 
        






        
# if run as main, run this diagnostic check
if __name__ == "__main__":
    print("DinoSting2 Test Code")
    print("version {0}, dated {1}".format(HGREVISION,HGDATE))
    print("last revised by {0}".format(HGAUTHOR))

    sting = DinoSting()

    print("0 degrees, 50/255 speed")
    sting.move(0)
    sting.fan(50)
    time.sleep(5)

    print("45 degrees, 0/255 speed")
    sting.move(45)
    sting.fan(0)
    time.sleep(5)

    print("90 degrees, 50/255 speed")
    sting.move(90)
    sting.fan(50)
    time.sleep(5)

    print("135 degrees, 0/255 speed")
    sting.move(135)
    sting.fan(0)
    time.sleep(5)

    print("180 degrees, 50/255 speed")
    sting.move(180)
    sting.fan(50)
    time.sleep(5)

    print("0 degrees, 0/255 speed")
    sting.gohome()
    print("Bye bye\n")


