#!/usr/bin/env python
'''
nano17.py
(c) 2012 Dennis Evangelista

Sketch of how nano17 code works. 
'''

import threading
import time
import logging
#logging.basicConfig(level=logging.DEBUG)

class Nano17():
  '''Nano17 object for interfacing with force sensor.'''
  def __init__(self,samples=10):
    self.devicename = "ATI Nano17 on NI PCI-6321"
    self.samplerate = 10000;
    self.samples = samples
    logging.debug("Nano17 object created")

  def setdurations(self,durations=1):
    '''Set duration (seconds) of Nano17 measurement'''
    self.samples = durations*self.samplerate
    logging.debug("Nano17 duration set to {0} s".format(durations))

  def acquire(self,samples=None):
    if (samples!=None):
      self.samples = samples
    logging.debug("Nano17.acquire() called, obtaining {0} samples".format(self.samples))
    data = ['X Y Z MX MY MZ fs=10000 averaging=16 fake','0 0 0 0 0 0']
    return data

  def __del__(self):
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
  print("Nano17 sketch code\n")

  nano = Nano17()
  trigger = threading.Event()
  trigger.clear()
  nano_task = Nano17Task(nano,trigger)
  nano_task.start()

  trigger.set()
  nano_task.dataready.wait()
  print("Got {0} lines:\n".format(len(nano_task.data)))
  print("\n".join(nano_task.data))

  nano_task.nano.setdurations(10)
  trigger.set()
  nano_task.dataready.wait()
  print("Got {0} lines:\n".format(len(nano_task.data)))
  print("\n".join(nano_task.data))
  
  nano_task.shutdown.set()
  print("Bye bye\n")


    
      
