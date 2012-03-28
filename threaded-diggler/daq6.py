#!/usr/bin/python
'''
daq6.py
(c) 2012 Dennis Evangelista

Updated version of daq5.py for Haas hardware, changes noted. 
'''

import ctypes
import numpy
import logging

nidaq = ctypes.windll.nicaiu # load the DLL for Windoze NT
#nidaq = ctypes.cdll.LoadLibrary("/Library/Frameworks/nidaqmxbase.framework/nidaqmxbase") # load it for Mac
# Similar syntax for Linux
# Mac version doesn't work

# setup some type definitions and constants to correspond with NI NIDAQmx.h
# typedefs
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32

# constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Diff = 10106
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_RSE = 10083 # NEED TO USE THIS WHEN USING ALTERNATE BOX SETUP
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0
DAQmx_Val_GroupByScanNumber = 1

def CHK(err):
    '''Check the return code of a NIDAQmx Base library call and throw
    an execption if it indicates failure.'''
    if err < 0:
        buf_size = 2048
        buf = ctypes.create_string_buffer('\000'*buf_size)
        nidaq.DAQmxGetExtendedErrorInfo(ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

class DAQcard():
    '''NI E6231 DAQ connected to ATI Nano17.'''
    
    def __init__(self, sampling_frequency=10000.0, samples=10, averaging=16):
        '''Constructor for a DAQ object.'''
        logging.debug("Creating DAQcard object")
        self.sampling_frequency = sampling_frequency
        self.samples = samples
        self.averaging = averaging
        self.nchannels = 6
        self.taskHandle=TaskHandle(0)
        self.data = numpy.zeros((self.samples,self.nchannels),dtype=numpy.float64)

        # Create DAQ task
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.taskHandle)))
        
        # Configure DAQ channel(s)
        CHK(nidaq.DAQmxCreateAIVoltageChan(self.taskHandle,
                                           "Dev1/ai0, Dev1/ai1, Dev1/ai2, Dev1/ai3, Dev1/ai4, Dev1/ai5",
                                           "SG0, SG1, SG2, SG3, SG4, SG5",
                                           DAQmx_Val_RSE,
                                           float64(-10.0),float64(10.0),
                                           DAQmx_Val_Volts, None))
        
        # Set DAQ sampling frequency
        CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle,"OnboardClock",float64(self.sampling_frequency),
                                        DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                        uInt64(self.samples*self.averaging+10)))

        logging.debug("DAQcard initialized")




    
    def acquire(self, samples=None):
        '''Acquires samples samples.'''
        if samples is None:
            samples = self.samples
        logging.debug("DAQcard acquiring {0} lines...".format(samples))
        self.data = numpy.zeros((samples,self.nchannels),dtype=numpy.float64)
        temp = numpy.zeros((samples*self.averaging,self.nchannels),dtype=numpy.float64)
        
        numread=int32()

        logging.debug(" asking for {0} numbers...".format(samples*self.averaging))
        # Next line sets DAQ sampling frequency
        CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle,"OnboardClock",float64(self.sampling_frequency),
                                        DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                        uInt64(samples*self.averaging+10)))
        # the last line can cause squirrely results if the samples-per-channel is wrong

        CHK(nidaq.DAQmxStartTask(self.taskHandle)) # Start NI DAQ
        CHK(nidaq.DAQmxReadAnalogF64(self.taskHandle, # Use this task
                                     DAQmx_Val_Cfg_Default, # Read until done
                                     float64(1800.0), # Time out after 30 min
                                     DAQmx_Val_GroupByScanNumber, # Don't interleave
                                     temp.ctypes.data, # Place in temp
                                     samples*self.nchannels*self.averaging, # Read this many samples
                                     ctypes.byref(numread), # Tell me how many I got
                                     None))
        logging.debug("DAQcard acquired {0} numbers for {1} channels, averaging {2}.".format(numread.value, self.nchannels, self.averaging))

        # this line does the averaging
        # had been wrong in previous instances
        for a in range(samples):
            self.data[a] = numpy.mean(temp[(a*self.averaging):((a+1)*self.averaging),:],axis=0)

        if self.taskHandle.value != 0:
            CHK(nidaq.DAQmxStopTask(self.taskHandle))
        return(self.data)


            
    def stop(self):
        '''Kills the DAQ task'''
        CHK(nidaq.DAQmxClearTask(self.taskHandle))
        logging.debug("DAQcard stopped")

    def __del__(self):
        self.stop()
        logging.debug("DAQcard garbage collected")



