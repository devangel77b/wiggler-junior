#!/usr/bin/env python
'''
tsensitivity.py
(c) 2012 Dennis Evangelista

Updated for Haas hardware
'''

import sonic
import nano17
import windtunnel
import threading
import logging
logging.basicConfig(level=logging.INFO)

import time
import os
#WIGGLERDIR = "~/Dropbox/turbulence-sensitivity-haas/anemo-sketch/RESULTS/"
WIGGLERDIR = "C:\\Users\\Dudley\\Desktop\\wiggler-junior\\RESULTS\\"

# Mercurial keywords disabled in Windoze7?
HGAUTHOR = '$Author$: devangel'.split()[1]
HGREVISION = '$Revision$: blah'.split()[1]
HGDATE = '$Date$: today'.split()[1]



class Measurement():
    '''Measurement object for doing a single measurement.'''
    def __init__(self,durations=10):
        self.measurementname = "Turbulence sensitivity"
        self.nanodata = []
        self.anemdata = []
        self.tunnel = windtunnel.WindTunnel()
        self.trigger = threading.Event()
        self.trigger.clear()
        self.anem_task = sonic.AnemometerTask(trigger=self.trigger)
        self.nano_task = nano17.Nano17Task(trigger=self.trigger)
        self.anem_task.anem.setdurations(durations)
        self.nano_task.nano.setdurations(durations)
        self.anem_task.start()
        self.nano_task.start()
        logging.debug("Measurement object created")

    def take(self,speed=0,angle=0,durations=10):
        logging.debug("Measurement.take() called")
        
        # Set model for next measurement
        self.tunnel.setangle(angle)
        self.tunnel.tunnelready.wait() # wait for servo to settle
        self.nano_task.nano.bias()

        # Set duration and start tunnel
        self.anem_task.anem.setdurations(durations)
        self.nano_task.nano.setdurations(durations)
        self.tunnel.setspeed(speed)
        self.tunnel.tunnelready.wait() # wait for speed to settle

        self.trigger.set() # signal start of data taking
        self.anem_task.dataready.wait()
        logging.debug("Got {0} lines of anem data".format(len(self.anem_task.data)))
        self.anemdata = self.anem_task.data
        self.nano_task.dataready.wait()
        logging.debug("Got {0} lines of nano data".format(len(self.nano_task.data)))
        self.nanodata = self.nano_task.data

        self.tunnel.setspeed(0) # secure fan
        self.tunnel.tunnelready.wait()
        logging.debug("Measurement.take() completed, coasting down")

    def save(self,path,nfilename,afilename):
        logging.debug("Measurement.save() called")

        logging.debug("Measurement.save() writing nano data to "+path+nfilename)
        f = open(path+nfilename,"w")
        f.write(self.nano_task.nano.headertext())
        numpy.savetxt(f,self.nanodata,delimiter=",")
        f.close
        logging.debug("     data saved to "+path+nfilename)

        logging.debug("Measurement.save() write anem data to "+path+afilename)
        f = open(path+afilename,"w")
        f.write(self.anem_task.anem.headertext())
        f.write("\n".join(anem_task.data))
        f.close
        logging.debug("     data saved to "+path+afilename)

        logging.debug("Measurement.save() completed")


    def __del__(self):
        self.nano_task.shutdown.set()
        self.anem_task.shutdown.set()
        self.tunnel = None
        logging.debug("Measurement object garbage collected")












class Replicates():
    '''Replicates object for running turbulence sensitivity measurements'''
    def __init__(self,modelname="test",number=1,angles=[0],speeds=range(0,255,50),durations=30):
        self.modelname = modelname
        self.number = number
        self.angles = angles
        self.reps = range(self.number)
        self.speeds = speeds
        self.durations=durations
        self.curdirname = WIGGLERDIR
        self.nfilename = "default_nano.csv"
        self.afilename = "default_anem.csv"

        self.meas = Measurement()
        logging.debug("Replicates object created")

    def setcurdirname(self):
        self.curdirname = WIGGLERDIR+time.strftime("%Y%m%d%H%M%S")+"\\"
        os.mkdir(self.curdirname)
        logging.debug("Replicates.setcurdirname set to {0}".format(self.curdirname))

    def setfilenames(self,angle=0,speed=0):
        temp = self.modelname+"_a"+format(angle)+"_s"+format(speed)
        self.nfilename = temp+"_nano.csv"
        self.afilename = temp+"_anem.csv"
        logging.debug("Replicates.setfilenames to "+temp)
        
    def go(self):
        logging.debug("Replicates.go() called")
        logging.info("Commencing replicates")
        for repcounter in self.reps:
            logging.info("Starting replicate {0} for model {1}".format(repcounter+1,self.modelname))
            self.setcurdirname()
            for angcounter in self.angles:
                logging.debug("Angle {0} degrees".format(angcounter))
                for spdcounter in self.speeds:
                    logging.debug("Speed {0}/255 units".format(spdcounter))
                    self.setfilenames(angcounter,spdcounter)
                    self.meas.take(spdcounter,angcounter,self.durations)
                    self.meas.save(self.curdirname,self.nfilename,self.afilename)
                    logging.info("     angle {0} degrees - speed {0}/255 units".format(angcounter,spdcounter))
            logging.info("Completed replicate {0}".format(repcounter+1))
        logging.info("Completed {0} replicates for model {1}, coasting down.".format(self.number, self.modelname))                   
  

    def __del__(self):
        self.meas = None
        logging.debug("Replicates object garbage collected")






# if run as main, run this diagnostic check
if __name__ == "__main__":
    print("Turbulence Sensitivity Test Code")
    print("version {0}, dated {1}".format(HGREVISION,HGDATE))
    print("last revised by {0}".format(HGAUTHOR))


    measurement = Measurement()
    measurement.take()
    measurement.save("foo","nanobar","anembar")
    measurement = None

    replicates = Replicates()
    replicates.go()
    replicates = None

    print("Bye bye\n")
