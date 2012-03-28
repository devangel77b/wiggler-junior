#!/usr/bin/env python
'''
nano17.py
(c) 2012 Dennis Evangelista

Updated version of Nano17 plus NI PCI 6231 DAQ
Now uses threading and logging and incorporates bug fixes
'''

import daq6
import ati_ft2
import numpy

import threading
import time
import logging
logging.basicConfig(level=logging.DEBUG)

# Mercurial keywords disabled in Windoze7?
HGAUTHOR = '$Author$: devangel'.split()[1]
HGREVISION = '$Revision$: blah'.split()[1]
HGDATE = '$Date$: today'.split()[1]


class Nano17():
  '''Nano17 object for interfacing with force sensor.'''
  def __init__(self,samples=10):
    self.devicename = "ATI Nano17 on NI PCI-6231"
    self.samplerate = 10000.0
    self.averaging=16
    self.effsamplerate = self.samplerate/self.averaging
    self.samples = samples

    self.daq = daq6.DAQcard(sampling_frequency=self.samplerate,samples=samples,averaging=self.averaging)
    self.cal = ati_ft2.ATIft("FT7695")
    logging.debug("Nano17 object created")

  def setdurations(self,durations=1):
    '''Set duration (seconds) of Nano17 measurement'''
    self.samples = durations*self.effsamplerate
    self.daq.samples = self.samples
    logging.debug("Nano17 duration set to {0} s".format(durations))

  def acquire(self,samples=None):
    if (samples==None):
      samples == self.samples
    logging.debug("Nano17.acquire() called, obtaining {0} samples".format(self.samples))
    data = self.daq.acquire(samples=samples) # collect the actual points
    cdata = self.cal(data) # apply calibration
    return cdata    

  def bias(self):
    logging.critical("Nano17 biasing, do not bump")
    y = self.daq.acquire(samples=500)
    meany = numpy.mean(y,axis=0)
    self.cal.bias(meany)

  def headertext(self):
    return "Force X (N),Force Y(N),Force Z (N),Torque X (N-mm),Torque Y (N-mm),Torque Z (N-mm),Frequency "+format(self.samplerate)+", Averaging Level = "+format(self.averaging)+", Effective Frequency "+format(self.effsamplerate)+", F/T Sensor = "+format(self.cal.calname)+", Time Started "+time.strftime("%m/%d/%Y %H:%M:%S")+"\n"

  def __del__(self):
    self.daq = None
    self.cal = None
    logging.debug("Nano17 garbage collected")

class Nano17Task(threading.Thread):
  '''Nano17Task thread for running and triggering concurrently'''
  def __init__(self,nano=None,trigger=None,samples=None):
    threading.Thread.__init__(self)
    self.daemon = True # allow program to exit with task running.
    if (nano == None):
      self.nano = Nano17()
    else: self.nano = nano
    if (samples!=None):
      self.nano.samples = samples
    if (trigger == None):
      self.trigger = threading.Event()
    else: self.trigger = trigger
    self.dataready = threading.Event()
    self.shutdown = threading.Event()
    self.trigger.clear()
    self.dataready.clear()
    self.shutdown.clear()
    self.data = []
    logging.debug("Nano17Task {0} created".format(self.name))
    
  def run(self):
    logging.debug("Nano17Task {0} running".format(self.name))
    while not(self.shutdown.is_set()):
      self.trigger.wait()
      logging.debug("Nano17Task {0} triggered at {1}".format(self.name,time.time()))
      self.dataready.clear()
      self.data = self.nano.acquire()
      self.dataready.set()
      self.trigger.clear()
    logging.debug("NanoTask {0} no longer alive".format(self.name))


# if run as main, run this diagnostic check
if __name__ == "__main__":
  print("ATI Nano17 Force Sensor and NI PCI6231 DAQ Test Code ")
  print("version {0}, dated {1}".format(HGREVISION,HGDATE))
  print("last revised by {0}".format(HGAUTHOR))

  nano = Nano17()
  trigger = threading.Event()
  trigger.clear()
  nano_task = Nano17Task(nano,trigger)
  nano_task.start()

  nano_task.nano.bias()

  trigger.set()
  nano_task.dataready.wait()
  print("Got {0} lines:\n".format(len(nano_task.data)))
  print(nano_task.data)
  nano_task.dataready.clear()
  time.sleep(10)
  
  nano_task.nano.setdurations(10)
  trigger.set()
  nano_task.dataready.wait()
  print("Got {0} lines:\n".format(len(nano_task.data)))
  print(nano_task.data)
  nano_task.dataready.clear()
  
  nano_task.shutdown.set()
  print("Bye bye\n")


    
      
