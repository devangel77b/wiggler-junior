#!/usr/bin/env python



import serial # needed for sting
import ctypes # needed for DAQcard
import numpy # needed for DAQcard and others
import xml.dom.minidom # needed for ati_ft

import dinosting # control of sting and wind tunnel speed
import daq5 # talks to ATI Nano17 via NI 6231 DAQ
import ati_ft # transforms etc related to ATI Nano17
import time
import os

# For twitter notification of completion
import tweepy
CONSUMER_KEY = 'LOJKetFhrPE4rBrYG5AbA'
CONSUMER_SECRET = 'yQrDO3seLdhQet8tpkpZYYSfqGXlXKAquII41iANg'
ACCESS_KEY = '216454340-xeb7SHIZcIBEUdVARkw0ru6GzqfYh9jAgkFI9Hy6'
ACCESS_SECRET = 'g5aLIf8dPUDEdTYH4cpxUk3iuMDh0DCEUQcloIDw'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# open the command prompt - this line by Leonard
filename = os.environ.get('PYTHONSTARTUP')
if filename and os.path.isfile(filename):
    execfile(filename)

