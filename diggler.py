#!/usr/bin/env python

# Main wind tunnel control

import serial # needed for DinoSting
import ctypes # needed for DAQcard
import numpy  # needed for DAQcard and others
import xml.dom.minidom # needed for ati_ft

import dinosting 
import daq5
import ati_ft
import time
import os

# None of these work so I wrote my own. 
#atidaqft = ctypes.windll.LoadLibrary('C:\\Program Files\\ATI Industrial Automation\\ATIDAQFT.NET\\atidaqft.dll')
#aticdaqft = ctypes.windll.LoadLibrary('C:\\Program Files\\ATI Industrial Automation\\ATIDAQFT.NET\\ATICombinedDAQFT.dll')
#atift = ctypes.cdll.LoadLibrary("C:\\Documents and Settings\\WindTunnel\\Desktop\\Dirk Wiggler\\ati_ft.so")
#atift = ctypes.cdll.LoadLibrary("C:\\Documents and Settings\\WindTunnel\\Desktop\\Dirk Wiggler\\ati_ft.dll")
#atidaqft = ctypes.windll.LoadLibrary('C:\\Program Files\\ATI DAQ FT\\atidaqft.dll')


class WindTunnel:
    def __init__(self):
        self.DAQ = daq5.DAQcard()
        self.Sting = dinosting.DinoSting(mount_angle=-15)
        self.Sting.gohome()
        self.Cal = ati_ft.ATIft('FT7695.cal')
        self.currentdata = None
        self.startuptime = 15
        print 'WindTunnel object created'

    def takedata(self,angle=0):
        self.Sting.move(angle) # set angle
        time.sleep(5)

        print 'Biasing - do not bump'
        y = self.DAQ.acquire(samples=100) # zero the sensor
        meany = numpy.mean(y, axis=0)
        self.Cal.bias(meany)

        self.Sting.fan(1) # turn on the fan

        print 'Waiting %d seconds for fan to startup' %(self.startuptime)
        time.sleep(self.startuptime) # Wait for fan to start up

        print 'Collecting data'
        y = self.DAQ.acquire() # collect the actual points
        self.currentdata = self.Cal(y) # apply calibration
        # apply averaging?? 

        self.Sting.fan(0) # secure fan
        print 'Data collected, coasting down'
        time.sleep(17)
#        return(self.currentdata)

    def save(self,filename):
        headertxt = "Force X (N),Force Y (N),Force Z (N), Torque X (N-mm), Torque Y (N-mm), Torque Z (N-mm), Frequency = 1000, Averaging Level = 16, F/T Sensor = FT7695, Time Started = " + time.strftime("%m/%d%Y %H:%M:%S") + "\n"
        f = open(filename,'w')
        f.write(headertxt)
        numpy.savetxt(f,self.currentdata,delimiter=',')
        f.close
        print 'Saved current data to {0}'.format(filename)

    def __del__(self):
        self.Sting = None
        self.DAQ = None
        self.Cal = None
        print 'WindTunnel object garbage collected.'


class Replicates:
    def __init__(self,modelname="test",number=5,angles=range(-15,95,5)):
        self.modelname = modelname
        self.number = number
        self.angles = angles
        self.reps = range(self.number)
        self.currentdir = None
        self.tunnel = WindTunnel()
        self.tunnel.Sting.move(0)
        self.tunnel.Sting.gohome()

    def warmup(self):
        print "Warming up fan"
        print "Use hot wire anemometer to check speed in range 5-6 m/s"
        self.tunnel.Sting.fan(1)
        time.sleep(120)
        self.tunnel.Sting.fan(0)
        
    def go(self):

        print "Commencing runs."
        for a in self.reps:
            print "Starting run %d"%(a)
            self.currentdir = "C:\\Documents and Settings\\WindTunnel\\Desktop\\"+time.strftime("%Y%m%d%H%M%S")+"\\"
            os.mkdir(self.currentdir)
            for b in self.angles:
                self.tunnel.takedata(b)
                filename = self.currentdir+self.modelname+"_"+str(b)+".csv"
                self.tunnel.save(filename)
            print "Completed run {0}".format(self.currentdir)
        print "Completed {0} runs for {1}".format(self.number, self.modelname)

    def __del__(self):
        self.tunnel = None
        print "Replicates object garbage collected."
        


                
            
        
