#!/usr/bin/env python
'''
windtunnel.py
(c) 2012 Dennis Evangelista

Sketch of how wind tunnel code works. 
'''

import dinosting2
import threading
import time
import logging
#logging.basicConfig(level=logging.DEBUG)

# Mercurial keywords disabled in Windoze7
HGAUTHOR = '$Author$: devangel'.split()[1]
HGREVISION = '$Revision$: blah'.split()[1]
HGDATE = '$Date$: today'.split()[1]








class WindTunnel():
  '''Anemometer object for interfacing with sonic.'''
  def __init__(self,tunnelready=None):
    self.devicename = "Engineering Laboratory Design Tunnel plus Robosting"
    if (tunnelready==None):
      self.tunnelready = threading.Event()
    else: self.tunnelready=tunnelready # at some point need to fix this
    self.tunnelready.clear()

    self.sting = dinosting2.DinoSting(mount_angle=0)
    self.speed = 0
    self.angle = 0
    self.fandelay = 15
    self.servodelay = 1

    self.setspeed(self.speed)
    self.setangle(self.angle)
    self.tunnelready.set()
    logging.debug("WindTunnel object created.")

  def setspeed(self,speed=0):
    '''Set wind tunnel speed in x/255 units'''
    logging.debug("WindTunnel set speed to {0}/255 units".format(speed))
    self.tunnelready.clear()
    self.speed = speed
    self.sting.fan(self.speed)
    logging.debug("     waiting {0} seconds for fan to reach speed".format(self.fandelay))
    time.sleep(self.fandelay)
    self.tunnelready.set()
    logging.debug("WindTunnel speed is now {0}/255 units".format(speed))

  def setspeedms(self,speedms=0):
    '''Not yet implemented'''
    self.tunnelready.clear()
#    self.speed = round(speedms*A+B)
#    check if in range 0 to 255
    self.tunnelready.set()
    logging.critical("NOT IMPLEMENTED: WindTunnel speed NOT set to {0} m/s".format(speedms))

  def setangle(self,angle=0):
    '''Set wind tunnel angle in degrees'''
    logging.debug("WindTunnel set angle to {0} degrees".format(angle))
    self.tunnelready.clear()
    self.angle = angle
    self.sting.move(self.angle)
    logging.debug("     waiting {0} seconds for servo to settle".format(self.servodelay))
    time.sleep(self.servodelay)
    self.tunnelready.set()
    logging.debug("WindTunnel set angle to {0} degrees".format(angle))

  def __del__(self):
    logging.debug("WindTunnel garbage collected")
    







# if run as main, run this diagnostic check
if __name__ == "__main__":
    print("WindTunnel test code")
    print("version {0}, dated {1}".format(HGREVISION,HGDATE))
    print("last revised by {0}".format(HGAUTHOR))

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


    
      
