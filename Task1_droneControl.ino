//CPS-Group1-task1
// Joystick library by Matthew Heironimus
// documentation of the Joystick library: https://github.com/MHeironimus/ArduinoJoystickLibrary
// download link: https://github.com/MHeironimus/ArduinoJoystickLibrary/releases/tag/v2.1.1

#include <Joystick.h>
Joystick_ Joystick;

int roll = A0;
int pitch = A1;
int button = 5;
int thrust = A3;
int yaw = A4;
int button2 = 12;

void setup() {
 
  // Initialize Joystick Library
  Joystick.begin(false);
  Joystick.setXAxisRange(0,1023); // set max range max->1023
  Joystick.setYAxisRange(0,1023);
  Joystick.setRxAxisRange(0,1023);
  Joystick.setRyAxisRange(0,1023);//thrust

  // next update: have pin numbers assigned to variables specific to the controller type(joystick, potentiometer etc..)
  pinMode(roll, INPUT);
  pinMode(pitch, INPUT);
  pinMode(button, INPUT);//button
  pinMode(button2, INPUT);//button
  pinMode(thrust, INPUT);// potentiometerL
  pinMode(yaw, INPUT);// potentiometerR
}

double roll_data, pitch_data, thrust_data, yaw_data;
int Sw, Sw2, lastbuttonstate[2]={0,0};
int untoggle = 0, toggle = 0;
void loop() {

  // read analog joystick values
  roll_data = analogRead(roll);
  pitch_data = analogRead(pitch);
  thrust_data = analogRead(thrust);//thrust
  yaw_data = analogRead(yaw);//yaw
  
  // set joystick data
  Joystick.setXAxis(roll_data);
  Joystick.setYAxis(pitch_data);
  Joystick.setRyAxis(thrust_data);//thrust
  Joystick.setRxAxis(yaw_data);//yaw

  int currButtonstate1 = digitalRead(button);
  if(currButtonstate1 != lastbuttonstate[0]){
    Joystick.setButton(0, Sw);
    lastbuttonstate[0] = currButtonstate1;
  }

  int currButtonstate2 = digitalRead(button2);
  if(currButtonstate2 != lastbuttonstate[1]){
    Joystick.setButton(1, Sw);
    lastbuttonstate[1] = currButtonstate2;
  }
  
    // send data to cf client
  Joystick.sendState();
}


