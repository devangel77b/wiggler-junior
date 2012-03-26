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