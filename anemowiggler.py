#!/usr/bin/env python
'''
anemowiggler.py
(c) 2011, 2012 Dennis Evangelista

Interface code for connecting to Young 81000 ultrasonic anemometer.
Does not currently implement configuration of the Young 81000, just reads.
Use a terminal emulation program to reconfigure the instrument.
'''



PORT = 'COM4' # for Windows7 machine in Haas
# PORT = '/dev/tty.KeySerial1' # for Mac
BAUD = 38400

# Mercurial update stuff
HGAUTHOR = '$Author$: devangel'.split()[1]
HGREVISION = '$Revision$: blah'.split()[1]
HGDATE = '$Date$: today'.split()[1]




import serial # need to talk to Sonic
import io # need this to use /r eol with Sonic
import threading # need to run sonic and ATI Nano17 concurrently
import time # for timing runs
import logging # nicer way to log
logging.basicConfig(level=logging.DEBUG)







class Anemometer():
    '''Anemometer object for interfacing with Young 81000 Sonic Anemometer'''
    def __init__(self,port=PORT,baud=BAUD):
        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            self.sio = io.TextIOWrapper(io.BufferedReader(self.ser),newline='\r')
            logging.debug("Anemometer connected on {0}.".format(port))
        except serial.SerialException:
            logging.critical("Anemometer could not connect on {0}, is it connected?".format(port))
            # Yonatan approves of use of .format - 2011-03-31 17:10 PDT
            
        self.devicename = 'Young 81000 Sonic Anemometer'
        self.samplerate = 32
        logging.debug("Anemometer created.")

    def acquire(self,samples=32):
        logging.debug("Anemometer.acquire() called, obtaining {0} samples.".format(samples))
        listoflines = []
        for i in xrange(samples):
            listoflines.append(self.sio.readline())
        return listoflines

    def __del__(self):
        del self.sio
        del self.ser
        logging.debug("Anemometer garbage collected.")







class AnemometerTask(threading.Thread):
    '''AnemometerTask thread for running and triggering an Anemometer'''
    def __init__(self, anem=None, trigger=None, samples=32):
        threading.Thread.__init__(self)
        self.daemon = True # allow program to exit with task running
        if (anem == None):
            self.anem = Anemometer()
        else: self.anem = anem
        self.samples = samples
        # configure signals to this task
        # can pass an external trigger to the task
        if (trigger == None): # trigger must be a valid threading.Event
            self.trigger = threading.Event()
        else: self.trigger = trigger
        # every task has a dataready flag, shutdown flag
        self.dataready = threading.Event()
        self.shutdown = threading.Event()
        # initialize signals
        self.trigger.clear()
        self.dataready.clear()
        self.shutdown.clear()
        self.data = [] # initialize data
        logging.debug("AnemometerTask {0} created.".format(self.name))

    def run(self):
        logging.debug("AnemometerTask {0} running".format(self.name))
        while not(self.shutdown.is_set()):
            self.trigger.wait()
            logging.debug("AnemometerTask {0} triggered at {1}.".format(self.name,time.time()))
            self.dataready.clear()
            self.data = self.anem.acquire(self.samples)
            self.dataready.set()
            self.trigger.clear()
            # loop infinitely checking if triggered and taking data. 
            # do I have to put a lock on data? 
        logging.debug("AnemometerTask {0} no longer alive".format(self.name))
        # shutown.is_set() so it's turning off. 




# need to implement dynamometer
# need to implement wind tunnel 
# need to implement turb sensitivity measurement






# If this is run as main program, do a diagnostic to check that it works. 
if __name__ == "__main__":
    print("Young 81000 Ultrasonic Anemometer Test Code")
    print("version {0}, dated {1}".format(HGREVISION,HGDATE))
    print("last revised by {0}".format(HGAUTHOR))

    anem = Anemometer()
    trigger = threading.Event()
    trigger.clear()
    anem_task = AnemometerTask(anem,trigger,samples=500)
    anem_task.start()

    trigger.set()
    anem_task.dataready.wait()
    print("\n Got {0} bytes:".format(len(anem_task.data)))
    print("\n".join(anem_task.data))
    
        
    anem_task.shutdown.set()
    print("Pythonic enough for you?")
    print("Bye bye.")
    
    
    

