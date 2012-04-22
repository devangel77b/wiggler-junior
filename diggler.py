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

# Setup twitter notification of completion
import tweepy
CONSUMER_KEY = 'LOJKetFhrPE4rBrYG5AbA'
CONSUMER_SECRET = 'yQrDO3seLdhQet8tpkpZYYSfqGXlXKAquII41iANg'
ACCESS_KEY = '216454340-xeb7SHIZcIBEUdVARkw0ru6GzqfYh9jAgkFI9Hy6'
ACCESS_SECRET = 'g5aLIf8dPUDEdTYH4cpxUk3iuMDh0DCEUQcloIDw'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# Open the Command Prompt
filename = os.environ.get('PYTHONSTARTUP')
if filename and os.path.isfile(filename):
    execfile(filename)

# None of these work so I wrote my own. 
#atidaqft = ctypes.windll.LoadLibrary('C:\\Program Files\\ATI Industrial Automation\\ATIDAQFT.NET\\atidaqft.dll')
#aticdaqft = ctypes.windll.LoadLibrary('C:\\Program Files\\ATI Industrial Automation\\ATIDAQFT.NET\\ATICombinedDAQFT.dll')
#atift = ctypes.cdll.LoadLibrary("C:\\Documents and Settings\\WindTunnel\\Desktop\\Dirk Wiggler\\ati_ft.so")
#atift = ctypes.cdll.LoadLibrary("C:\\Documents and Settings\\WindTunnel\\Desktop\\Dirk Wiggler\\ati_ft.dll")
#atidaqft = ctypes.windll.LoadLibrary('C:\\Program Files\\ATI DAQ FT\\atidaqft.dll')


class WindTunnel:
    def __init__(self):
        self.DAQ = daq5.DAQcard()
        self.Sting = dinosting.DinoSting(mount_angle=0)
        self.Sting.gohome()
        self.Cal = ati_ft.ATIft('FT10452.cal')
        self.currentdata = None
        self.startuptime = 15
        print 'WindTunnel object created'

    def takedata(self,speed,angle=0):
        self.Sting.move(angle) # set angle
        time.sleep(5)

        print 'Biasing - do not bump'
        y = self.DAQ.acquire(samples=100) # zero the sensor
        meany = numpy.mean(y, axis=0)
        self.Cal.bias(meany)

        self.Sting.fan(speed) # turn on the fan

        print 'Waiting %d seconds for fan to startup' %(self.startuptime)
        time.sleep(self.startuptime) # Wait for fan to start up

        print 'Collecting data'
        y = self.DAQ.acquire() # collect the actual points
        self.currentdata = self.Cal(y) # apply calibration
     
        self.Sting.fan(0) # secure fan
        print 'Data collected, coasting down'
        time.sleep(17)

    def save(self,filename):
        headertxt = "Force X (N),Force Y (N),Force Z (N), Torque X (N-mm), Torque Y (N-mm), Torque Z (N-mm), Frequency = 1000, Averaging Level = 8, F/T Sensor = FT7695, Time Started = " + time.strftime("%m/%d%Y %H:%M:%S") + "\n"
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
    def __init__(self,modelname="test",number=5,angles=range(-15,95,5),speed=0):
        self.modelname = modelname
        self.number = number
        self.angles = angles
        self.reps = range(self.number)
        self.currentdir = None
        self.tunnel = WindTunnel()
        self.tunnel.Sting.move(0)
        self.tunnel.Sting.gohome()
        self.speed = speed

    def warmup(self):
        print "Warming up fan"
        print "Use hot wire anemometer to check speed in range 5-6 m/s"
        self.tunnel.Sting.fan(self.speed)
        time.sleep(20)
        self.tunnel.Sting.fan(0)

    def go(self):

        print "Commencing runs."
     #   twitterstatus = "Starting {0} runs of {1}".format(self.number, self.modelname)
     #   api.update_status(twitterstatus)
        for a in self.reps:
            print "Starting run %d"%(a)
            self.currentdir = "C:\\Users\\Dudley\\Desktop\\wiggler-junior\\RESULTS\\"+time.strftime("%Y%m%d%H%M%S")+"\\"
            os.mkdir(self.currentdir)
            for b in self.angles:
                self.tunnel.takedata(self.speed,b)
                filename = self.currentdir+self.modelname+"_n"+str(a)+"_a"+str(b)+"_s"+str(self.speed)+".csv"
                self.tunnel.save(filename)
            print "Completed run {0}".format(a)
    #        twitterstatus = "Completed replicate {0} of {1} for {2}".format(a+1,self.number, self.modelname)
    #        api.update_status(twitterstatus)

        print "Completed {0} runs for {1}".format(self.number, self.modelname)
        twitterstatus = "Completed {0} runs of {1}.  Please load a new model.".format(self.number, self.modelname)
        api.update_status(twitterstatus)

    def __del__(self):
        self.tunnel = None
        print "Replicates object garbage collected."



class yawReplicates(Replicates):
    def __init__(self,modelname="test",number=5,angles=range(-30,35,5),speed=0):
        Replicates.__init__(self,modelname,number,angles,speed)
        self.tunnel.Sting.mount_angle = -90
        print "yawReplicates object created"

    def __del__(self):
        print "Garbage collecting yaw replicates object"
        
                                                           
																																
class reynoldsReplicates(Replicates):
    def __init__(self,modelname="test",number=5,angle=30,speeds=[0]):
        Replicates.__init__(self,modelname,number)
        self.angle = angle
        self.speeds = speeds
        self.tunnel.Sting.mount_angle = 0
        self.tunnel.Sting.move(0)
        print "reynoldsReplicates object created"

    def __del__(self):
        print "Garbage collecting reynolds replicates object"

    def go(self):

        print "Commencing runs."
        self.currentdir = "C:\\Users\\Dudley\\Desktop\\wiggler-junior\\RESULTS\\"+time.strftime("%Y%m%d%H%M%S")+"\\"
        os.mkdir(self.currentdir)
        
        self.tunnel.Sting.move(self.angle) # set angle
        time.sleep(5)

        print 'Biasing - do not bump'
        y = self.tunnel.DAQ.acquire(samples=100) # zero the sensor
        meany = numpy.mean(y, axis=0)
        self.tunnel.Cal.bias(meany)

        for a in range(len(self.speeds)):
            # print "Please set dial to %d."%(a)
            # dial = int(raw_input('dial = ?'))
            
            dial = self.speeds[a]

            self.tunnel.Sting.fan(dial) # turn on the fan
            print 'Waiting %d seconds for fan to startup' %(self.tunnel.startuptime)
            print 'Be sure to check wind speed with anemometer'
            time.sleep(self.tunnel.startuptime) # Wait for fan to start up
                    
            for b in range(self.number):
               
                print 'Collecting data'
                y = self.tunnel.DAQ.acquire() # collect the actual points
                self.tunnel.currentdata = self.tunnel.Cal(y) # apply calibration
                filename = self.currentdir+self.modelname+"_n"+str(b)+"_a"+str(self.angle)+"_s"+str(dial)+".csv"
                self.tunnel.save(filename)
    
            print "Completed run at dial {0}".format(a)
    
        self.tunnel.Sting.fan(0) # secure fan
        print 'Data collected, coasting down'
        time.sleep(17)
        print "Completed {0} runs for {1}".format(self.number, self.modelname)
       # twitterstatus = "Completed {0} runs of {1}.  Please load a new model.".format(self.number, self.modelname)
       # api.update_status(twitterstatus)
       
class multiReplicates(Replicates):
    def __init__(self,modelname="test",number=5,angles=range(0,181,10),speeds=[0]):
        Replicates.__init__(self,modelname,number)
        self.angles = angles
        self.speeds = speeds
        self.tunnel.Sting.mount_angle = 0
        self.tunnel.Sting.move(0)
        print "reynoldsReplicates object created"

    def __del__(self):
        print "Garbage collecting reynolds replicates object"

    def go(self):

        print "Commencing runs."
        self.currentdir = "C:\\Users\\Dudley\\Desktop\\wiggler-junior\\RESULTS\\"+time.strftime("%Y%m%d%H%M%S")+"\\"
        os.mkdir(self.currentdir)
        
        print 'Biasing - do not bump'
        y = self.tunnel.DAQ.acquire(samples=100) # zero the sensor
        meany = numpy.mean(y, axis=0)
        self.tunnel.Cal.bias(meany)

        for a in range(len(self.speeds)):
            for b in self.angles:
                # print "Please set dial to %d."%(a)
                # dial = int(raw_input('dial = ?'))
                
                self.tunnel.Sting.move(b); # set angle
                time.sleep(5)
                
                dial = self.speeds[a]

                self.tunnel.Sting.fan(dial) # turn on the fan
                print 'Waiting %d seconds for fan to startup' %(self.tunnel.startuptime)
                print 'Be sure to check wind speed with anemometer'
                time.sleep(self.tunnel.startuptime) # Wait for fan to start up
                        
                for c in range(self.number):
                   
                    print 'Collecting data'
                    y = self.tunnel.DAQ.acquire() # collect the actual points
                    self.tunnel.currentdata = self.tunnel.Cal(y) # apply calibration
                    filename = self.currentdir+self.modelname+"_n"+str(c)+"_a"+str(b)+"_s"+str(dial)+".csv"
                    self.tunnel.save(filename)
        
                print "Completed run at dial {0} and angle {1}".format(a,b)
    
        self.tunnel.Sting.fan(0) # secure fan
        print 'Data collected, coasting down'
        time.sleep(17)
        print "Completed {0} runs for {1}".format(self.number, self.modelname)
       # twitterstatus = "Completed {0} runs of {1}.  Please load a new model.".format(self.number, self.modelname)
       # api.update_status(twitterstatus)
       
print "***********************"
print "Diggler-Junior, version 2"
print ""
print "Replicate objects you can create are"
print "> Replicates(modelname=\"test\",number=5,angles=range(-15,95,5),speed=0)"
print "> yawReplicates(modelname=\"test\",number=5,angles=range(-30,35,5),speed=0)"
print "> reynoldsReplicates(modelname=\"test\",number=5,angle=30,speeds=[0])"
print "> multiReplicates(modelname=\"test\",number=5,angle=range(0,181,10),speeds=[0])"
print "methods for all Replicates are warmup() and go()"
print "***********************"