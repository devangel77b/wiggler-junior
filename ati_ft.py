#!/usr/bin/env python

import xml.dom.minidom
import numpy

class ATIft:
    def __init__(self,calfilename='FT10452.cal'):
        print 'Created ATIft object'
        self.calfilename = calfilename

        self.calDOM = xml.dom.minidom.parse(calfilename)

        self.calFTSensor = self.calDOM.documentElement
        self.Serial = str(self.calFTSensor.getAttribute("Serial"))
        self.BodyStyle = str(self.calFTSensor.getAttribute("BodyStyle"))
        self.Family = str(self.calFTSensor.getAttribute("Family"))
        self.NumGages = int(self.calFTSensor.getAttribute("NumGages"))
        self.CalFileVersion = str(self.calFTSensor.getAttribute("CalFileVersion"))

        self.calCalibration = self.calFTSensor.getElementsByTagName("Calibration")[0]
        self.PartNumber = str(self.calCalibration.getAttribute("PartNumber"))
        self.CalDate = str(self.calCalibration.getAttribute("CalDate"))
        self.ForceUnits = str(self.calCalibration.getAttribute("ForceUnits"))
        self.TorqueUnits = str(self.calCalibration.getAttribute("TorqueUnits"))
        self.DistUnits = str(self.calCalibration.getAttribute("DistUnits"))
        self.OutputMode = str(self.calCalibration.getAttribute("OutputMode"))
        self.OutputRange = float(self.calCalibration.getAttribute("OutputRange"))
        self.HWTempComp = bool(self.calCalibration.getAttribute("HWTempComp"))
        self.GainMultiplier = float(self.calCalibration.getAttribute("GainMultiplier"))
        self.CableLossDetection = bool(self.calCalibration.getAttribute("CableLossDetection"))
        self.OutputBipolar = bool(self.calCalibration.getAttribute("OutputBipolar"))

        self.BasicTransform = self.calCalibration.getElementsByTagName("BasicTransform")[0]
        self.tooltransform = numpy.zeros(6)
        self.tooltransform[0] = float(self.BasicTransform.getAttribute("Dx"))
        self.tooltransform[1] = float(self.BasicTransform.getAttribute("Dy"))
        self.tooltransform[2] = float(self.BasicTransform.getAttribute("Dz"))
        self.tooltransform[3] = float(self.BasicTransform.getAttribute("Rx"))
        self.tooltransform[4] = float(self.BasicTransform.getAttribute("Ry"))
        self.tooltransform[5] = float(self.BasicTransform.getAttribute("Rz"))
        
        self.axislist = self.calCalibration.getElementsByTagName("Axis")

        self.max = numpy.zeros(6)
        self.scale = numpy.zeros(6)
        self.BasicMatrix = numpy.zeros((6,6))
        for i in range(0,6):
            self.max[i] = float(self.axislist[i].getAttribute("max"))
            self.scale[i] = float(self.axislist[i].getAttribute("scale"))
            temp = str(self.axislist[i].getAttribute("values"))
            tempvals = temp.split()    
            for j in range(0,6):
                self.BasicMatrix[i,j] = float(tempvals[j])/self.scale[i]

        self.TTM = numpy.zeros((6,6))
        self.TTM[0,0] = 1.0
        self.TTM[1,1] = 1.0
        self.TTM[2,2] = 1.0
        self.TTM[3,3] = 1.0
        self.TTM[4,4] = 1.0
        self.TTM[5,5] = 1.0
        self.TTM[3,1] = float(self.tooltransform[2])
        self.TTM[4,0] = -float(self.tooltransform[2])

        self.calmatrix = numpy.dot(self.TTM,self.BasicMatrix)
        self.biasvoltage = numpy.zeros(6)        

    def bias(self,x):
        print 'Set bias voltage'
        print x
        self.biasvoltage = x

    def unbias(self):
        self.biasvoltage = numpy.zeros(6)

    def __call__(self,x):
        return(numpy.transpose(numpy.dot(self.calmatrix,numpy.transpose(x-self.biasvoltage))))
                
    def __del__(self):
        print 'Garbage collected ATIft object'

