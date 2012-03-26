Plug in the Arduino to the USB port and power outlet.
Turn on the power supply connected to the splitter.
Load the wind tunnel plug with the hole for the wires horizontal on the right side.
Plug the red connector to the long red connector on top of the wind tunnel.
Plug the green connector to the wind tunnel plug.
Go to the panel
    [MON] > Basic Parameters Group > FMod > Terminal
                                   > CMod > Terminal
    If you do it the other way, turn the frequency down to zero.
    
To use the code, open the file named START.
>> import diggler
>> test = diggler.Replicates(modelname ...)
>> test.tunnel.Sting.gohome()
>> test.go()
Wait until it ends.
The results are in the RESULTS folder.

When finished with everything, go to the panel
    [MON] > Basic Parameters Group > CMod > Panel
                                   > FMod > Panel




To check windspeed calibration

import diggler
test = diggler.Replicates()
test.tunnel.Sting.fan(255)

or whatever speed you want. 
Calibration on 2012-03-26

byte speed.mps replicate
0 0 1
25 0.43 1
50 1.03 1
75 1.63 1
100 2.23 1
125 2.90 1
150 3.71 1
175 4.51 1
200 5.25 1
225 6.00 1
250 6.75 1
255 6.90 1