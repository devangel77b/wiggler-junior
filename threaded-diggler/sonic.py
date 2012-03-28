#!/usr/bin/env python
'''
sonic.py
(c) 2012 Dennis Evangelista

Sketch of how sonic anemometer code works. 
'''

import threading
import time
import logging
#logging.basicConfig(level=logging.DEBUG)

PORT = 'COM4'
BAUD = 38400
import serial
import io

# Mercurial keywords disabled in Windoze7
HGAUTHOR = '$Author$: devangel'.split()[1]
HGREVISION = '$Revision$: blah'.split()[1]
HGDATE = '$Date$: today'.split()[1]

class Anemometer():
  '''Anemometer object for interfacing with sonic.'''
  def __init__(self,samples=10,port=PORT,baud=BAUD):
    try:
      self.ser = serial.Serial(port,baud,timeout=0.1)
      self.sio = io.TextIOWrapper(io.BufferedReader(self.ser),newline="\r")
      logging.debug("Anemometer connected on {0} at {1} baud".format(port,baud))
    except serial.SerialException:
      logging.critical("Anemometer could not connect on {0}, is it connected?".format(port))

    self.devicename = "Young 81000 Sonic Anemometer"
    self.samplerate = 32
    self.samples = samples
    logging.debug("Anemometer object created")

  def setdurations(self,durations=1):
    '''Set duration (seconds) of anemometer measurement'''
    self.samples = durations*self.samplerate
    logging.debug("Anemometer duration set to {0} s".format(durations))

  def acquire(self,samples=None):
    if (samples!=None):
      self.samples = samples
    logging.debug("Anemometer.acquire() called, obtaining {0} samples".format(self.samples))
    listoflines = []
    for i in xrange(samples):
      listoflines.append(self.sio.readline())
    return listoflines

  def __del__(self):
    del self.sio
    del self.ser
    logging.debug("Anemometer garbage collected")






class AnemometerTask(threading.Thread):
    '''AnemometerTask thread for running and triggering concurrently'''
    def __init__(self,anem=None,trigger=None,samples=None):
        threading.Thread.__init__(self)
        self.daemon = True # allow program to exit with task running.
        if (anem == None):
            self.anem = Anemometer()
        else: self.anem = anem
        if (samples!=None):
            self.anem.samples = samples
        if (trigger == None):
            self.trigger = threading.Event()
        else: self.trigger = trigger
        self.dataready = threading.Event()
        self.shutdown = threading.Event()
        self.trigger.clear()
        self.dataready.clear()
        self.shutdown.clear()
        self.data = []
        logging.debug("AnemometerTask {0} created".format(self.name))

    def run(self):
        logging.debug("AnemometerTask {0} running".format(self.name))
        while not(self.shutdown.is_set()):
            self.trigger.wait()
            logging.debug("AnemometerTask {0} triggered at {1}".format(self.name,time.time()))
            self.dataready.clear()
            self.data = self.anem.acquire()
            self.dataready.set()
            self.trigger.clear()
        logging.debug("AnemometerTask {0} no longer alive".format(self.name))







# if run as main, run this diagnostic check
if __name__ == "__main__":
    print("Young 81000 Ultrasonic Anemometer Test Code")
    print("version {0}, dated {1}".format(HGREVISION,HGDATE))
    print("last revised by {0}".format(HGAUTHOR))

    anem = Anemometer()
    trigger = threading.Event()
    trigger.clear()
    anem_task = AnemometerTask(anem,trigger)
    anem_task.start()

    trigger.set()
    anem_task.dataready.wait()
    print("Got {0} line:\n".format(len(anem_task.data)))
    print("\n".join(anem_task.data))

    anem_task.anem.setdurations(10)
    trigger.set()
    anem_task.dataready.wait()
    print("Got {0} line:\n".format(len(anem_task.data)))
    print("\n".join(anem_task.data))

    anem_task.shutdown.set()
    print("Bye bye\n")


    
      
