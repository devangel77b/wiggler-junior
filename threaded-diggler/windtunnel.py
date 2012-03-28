#!/usr/bin/env python
'''
windtunnel.py
(c) 2012 Dennis Evangelista

Sketch of how wind tunnel code works. 
'''

import threading
import logging
#logging.basicConfig(level=logging.DEBUG)

class WindTunnel():
  '''Anemometer object for interfacing with sonic.'''
  def __init__(self,tunnelready=None):
    self.devicename = "Engineering Laboratory Design Tunnel plus Robosting"
    if (tunnelready==None):
      self.tunnelready = threading.Event()
    else: self.tunnelready=tunnelready # at some point need to fix this
    self.tunnelready.clear()
    self.speed = 0
    self.angle = 0
    self.tunnelready.set()
    logging.debug("WindTunnel object created.")

  def setspeed(self,speed=0):
    '''Not yet implemented'''
    self.tunnelready.clear()
    self.speed = speed
    self.tunnelready.set()
    logging.debug("WindTunnel set speed to {0}/255 units".format(speed))

  def setspeedms(self,speedms=0):
    '''Not yet implemented'''
    self.tunnelready.clear()
    self.speed = speedms
    self.tunnelready.set()
    logging.debug("WindTunenl set speed to {0} m/s".format(speedms))

  def setangle(self,angle=0):
    '''Not yet implemented'''
    self.tunnelready.clear()
    self.angle = angle
    self.tunnelready.set()
    logging.debug("WindTunnel set angle to {0} degrees".format(angle))

  def __del__(self):
    logging.debug("WindTunnel garbage collected")
    

# if run as main, run this diagnostic check
if __name__ == "__main__":
    print("WindTunnel sketch code\n")

    tunnel = WindTunnel()
    print("tunnel was created")

    tunnel.setspeed(100)
    tunnel.setspeed(0)
    tunnel.setspeedms(1)
    tunnel.setspeedms(0)
    tunnel.setangle(90)
    tunnel.setangle(0)

    tunnel.tunnelready.wait()
    print("waited for tunnel to be ready, then did stuff")

    tunnel = None
    print("Bye bye")


    
      
