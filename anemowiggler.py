#!/usr/bin/env python
'''
sonic.py
(c) 2011, 2012 Dennis Evangelista

Interface code for connecting to Young 81000 ultrasonic anemometer.
Does not currently implement configuration of the Young 81000, just reads.
Use a terminal emulation program to reconfigure the instrument.
'''



PORT = 'COM4' # for Windows7 machine in Haas
# PORT = '/dev/tty.KeySerial1' # for Mac
BAUD = 38400

# Mercurial update stuff
HGAUTHOR = '$Author$'.split()[1]
HGREVISION = '$Revision$'.split()[1]
HGDATE = '$Date$'.split()[1]




import serial # need to talk to Sonic
import threading # need to run sonic and ATI Nano17 concurrently
import time # for timing runs
import logging # nicer way to log

# Setup logging
sonic_nullhandler = logging.NullHandler()
sonic_logger = logging.getLogger("sonic").addHandler(sonic_nullhandler)






class Anemometer():
    '''Anemometer object for interfacing with Young 81000 Sonic Anemometer'''
    def __init__(self,port=PORT,baud=BAUD):
        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            logging.debug("Anemometer connected on {0}.".format(port))
        except serial.SerialException:
            logging.critical("Anemometer could not connect on {0}, is it connected?".format(port))
            # Yonatan approves of use of .format - 2011-03-31 17:10 PDT
            
        self.devicename = 'Young 81000 Sonic Anemometer'
        self.samplerate = 32
        logging.debug("Anemometer created.")

    def acquire(self,samples=32):
        logging.debug("Anemometer.acquire() called, obtaining {0} samples.".format(samples))
        return self.ser.read(samples)

    def __del__(self):
        del self.ser
        logging.debug("Anemometer garbage collected.")







class AnemometerTask(threading.Thread):
    '''AnemometerTask thread for running and triggering an Anemometer'''
    def __init__(self, anem=None, trigger=None, samples=32):
        threading.Thread.__init__(self)
        self.daemon = True
        if (anem == None):
            self.anem = Anemometer()
        else: self.anem = anem
        self.samples = samples
        if (trigger == None):
            self.trigger = threading.Event()
        else: self.trigger = trigger
        self.dataready = threading.Event()
        self.shutdown = threading.Event()
        self.trigger.clear()
        self.dataready.clear()
        self.shutdown.clear()
        self.data = None
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
        logging.debug("AnemometerTask {0} no longer alive".format(self.name))








if __name__ == "__main__":
    print("Young 81000 Ultrasonic Anemometer Test Code")
    print("version {0}, dated {1}".format(HGREVISION,HGDATE))
    print("last revised by {0}".format(HGAUTHOR))

    anem = Anemometer()
    trigger = threading.Event()
    trigger.clear()
    anem_task = AnemometerTask(anem,trigger,samples=1000)
    anem_task.start()

    trigger.set()
    anem_task.dataready.wait()
    print("\n Got {0} bytes:".format(len(anem_task.data)))
    print("\n".join(anem_task.data.split("\r")))
        
    anem_task.shutdown.set()
    print("Pythonic enough for you?")
    print("Bye bye.")
    
    
    

