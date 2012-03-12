/* 
DinoStingFan

Controls dinosaur positioning sting and fan for Microraptor 
gui experiments in 4115 VLSB, UC Berkley Department of Integrative
Biology. 

Dependencies:
Arduino 0017 or higher
Python servo.py or similar code - see Dirk Wiggler

Created:  10 November 2010
Author:   Dennis Evangelista
Version:  0.1
License:  GPLv3

*/


// Import the Arduino Servo library
#include <Servo.h>

// Create a Servo object for the sting
Servo servo1;

// Servo startup values for Hitec HS5485HB
// If servo is changed must check these values
int minPulse = 850;   // us, minimum servo position 0 degrees
int maxPulse = 1900;  // us, maximum servo position 180 degrees
int ServoPin = 9;     // Servo is connected to Pin 9 on Dirk Board

int   FanPin = 5;    // Fan relay is connected to Pin 5.


// User input for servo and position
int userInput[3];     // Raw input from serial buffer, 3 bytes
int startbyte;        // start byte, begin reading input
int whichdevice;      // which device to use
int fanspeed;         // speed to set the fan
int pos;              // servo position, angle 0-180
int i;                // iterator



// Setup Arduino on startup
void setup()
{
  servo1.attach(ServoPin,minPulse,maxPulse);
  // Attaches servo to pin 9 and sets pulse timing for Hitec
  
  pinMode(FanPin,OUTPUT);
  
  // Sets fan as an output pin 11
  
  Serial.begin(9600);
  // Establishes serial connection with main computer
}



// Loop infinitely.  Listen for bytes on serial port and 
// jiggle servo or fan as necessary. 
void loop()
{
  // Wait for serial input (min 3 bytes in buffer)
  if (Serial.available() > 2){
    startbyte = Serial.read(); // Read first byte
    
    if (startbyte == 255){
        userInput[0] = Serial.read();
        userInput[1] = Serial.read();
      }
      
      whichdevice = userInput[0];
      pos = userInput[1];
      
      //if (pos==255) {whichdevice = 255;}
      
      switch(whichdevice){
        case 1: // servo positioning command
          servo1.write(pos);  // write sting position
          break;
          
        case 2: // fan relay command
          analogWrite(FanPin,pos); // change fan speed
          break;
      } // switch servo
    } // if start byte detected
  } // if serial available
} // loop()


