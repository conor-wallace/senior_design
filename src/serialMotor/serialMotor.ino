#include <Stepper.h>
#include <Servo.h>
#include <math.h>
#include <ros.h>
#include <std_msgs/String.h>
#include <std_msgs/Float32.h>

//istantiate 5 motors
#define stepsPerRevolution  1000
#define degreesPerStep       11.125
Stepper M_base(stepsPerRevolution, 4, 5);
Stepper M_shoulder(stepsPerRevolution, 6, 7);
Stepper M_elbow(stepsPerRevolution, 8, 9);
Stepper M_wrist(stepsPerRevolution, 10, 11);
Stepper M_elbowWrist(stepsPerRevolution, 8, 9, 10, 11);//simultaniously moves elbow and wrist equal and inversely
Servo M_claw;

//stores the position of the limbs of the arm
double shoulder_degree;
double elbow_degree;
double wrist_degree;
double base_offset;
int ServoPos = 0;

//universal index
int i;

//These defines will stand the arm straigt up and wrist at 45 degrees as a default
//degrees are measured from positive y-axis
#define shoulder_default  0
#define elbow_default     0
#define wrist_default     0
#define base_default      0

//ros istantiations and variables
ros::NodeHandle  nh;
String kobukiLocation;
String requestedObject;
String armStatus;
double reach_dist = 0; //how far away the obj is from the camera
int distFristRead = 0;
double err_offset = 0; //how far the object is from the center of camera
int centerFristRead = 0;
double obj_width = 0;
int widthFristRead = 0;
boolean rosOn = false;

void kobukiCb( const std_msgs::String& msg){
  kobukiLocation = msg.data;
}

void objectCb( const std_msgs::String& msg){
  requestedObject = msg.data;
}

void distanceCb( const std_msgs::Float32& msg){
  if(distFristRead == 0){
    reach_dist = msg.data;
  }
  distFristRead = 1; 
}

void centerCb( const std_msgs::Float32& msg){
  if(centerFristRead == 0){
    err_offset = msg.data;
  }
  centerFristRead = 1;
}

void bbwidthCb( const std_msgs::Float32& msg){
  if(widthFristRead == 0){
    obj_width = msg.data;
  }
  widthFristRead = 1;
}

ros::Subscriber<std_msgs::String> sub1("kobuki_location", kobukiCb );
ros::Subscriber<std_msgs::String> sub2("object", objectCb );
ros::Subscriber<std_msgs::Float32> sub3("distance", distanceCb );
ros::Subscriber<std_msgs::Float32> sub4("center_image", centerCb );
ros::Subscriber<std_msgs::Float32> sub5("bounding_box_width", bbwidthCb );
//ros::Publisher<std_msgs::String> sub3("arm_status", objectCb );
std_msgs::String str_msg;
ros::Publisher chatter("chatter", &str_msg);


void setup()
{
  //motor setup
  M_claw.attach(3);
  M_base.setSpeed(60);
  M_shoulder.setSpeed(60);
  M_elbow.setSpeed(60);
  M_wrist.setSpeed(60);
 
  //ros setup
  nh.initNode();
  nh.advertise(chatter);
  nh.subscribe(sub1);
  nh.subscribe(sub2);
 
  //motor status communication setup
  Serial.begin(4800);
}


void loop()
{
  
  if (rosOn) {str_msg.data = "Starting..."; chatter.publish(&str_msg);}
  Serial.println("Starting...");
  if (rosOn) while(kobukiLocation != "pickup") {} //wait for start flag
  if (!rosOn) startCalibration();
  //move base, shoulder, elbow, and wrist (respectively) to defined degrees
  center(err_offset);
  moveToDegree(0,40,90,-40);
  reach(1);
  grabWaitDrop();
  armReset();
  
  //not sure what this does
  chatter.publish( &str_msg );
  nh.spinOnce();
  delay(500);
}

void center(double offset)
{
  double base_steps = offset/degreesPerStep;
  if (offset > 0) //too far right
  {
    stepForward(M_base, &base_offset);
    base_offset+=base_steps*degreesPerStep;
  }
  if (offset < 0) //too far left
  {
    base_steps = abs(base_steps);
    stepBackward(M_base, &base_offset);
    base_offset-=base_steps*degreesPerStep;
  }
}

void reach(int dist)
{
  dist = dist-18;
  //double shoulder_steps=dist/2;
  double elbow_steps=dist/2;
  double wrist_steps=elbow_steps;
 
  if (dist > 0)
  {
    stepBackward(M_elbow, &elbow_steps);
    elbow_degree-=elbow_steps*degreesPerStep;

    //stepForward(M_shoulder, &shoulder_steps);
    //shoulder_degree+=shoulder_steps*degreesPerStep;
   
    stepForward(M_wrist, &wrist_steps);
    wrist_degree+=wrist_steps*degreesPerStep;
   
  }
  else if(dist < 0)
  {
    //stepBackward(M_shoulder, &shoulder_steps);
    //shoulder_degree-=shoulder_steps*degreesPerStep;
   
    stepForward(M_elbow, &elbow_steps);
    elbow_degree+=elbow_steps*degreesPerStep;
   
    stepBackward(M_wrist, &wrist_steps);
    wrist_degree=wrist_steps*degreesPerStep;
  }

    Serial.println("Shoulder now at");
    Serial.print(shoulder_degree);
    Serial.print(" degrees\n");
    Serial.println("Elbow now at");
    Serial.print(elbow_degree);
    Serial.print(" degrees\n");
}


void closeClaw()
{
  for(ServoPos = 75; ServoPos < 180; ServoPos += 1)  // goes from 0 degrees to 180 degrees 
  { // in steps of 1 degree 
    
    M_claw.write(ServoPos);              // tell servo to go to position in variable 'pos' 
    delay(15);                       // waits 15ms for the servo to reach the position 
  }
  delay(3000);
}

void openClaw()
{
  for(ServoPos = 180; ServoPos>=75; ServoPos-=1)     // goes from 180 degrees to 0 degrees 
  {                                
    M_claw.write(ServoPos);              // tell servo to go to position in variable 'pos' 
    delay(15);                       // waits 15ms for the servo to reach the position 
  }
  delay(3000);
}

void armReset()
{
  moveToDegree(base_default, shoulder_default+12, elbow_default+12, wrist_default+12);
}

void moveToDegree(double base_dest, double shoulder_dest, double elbow_dest, double wrist_dest)
{
  
  //gather location destinations in degrees    && 
  //calculation of the distance need to travel
  double base_diff = base_dest - base_offset;
  double base_steps = (base_diff/degreesPerStep);
  Serial.print("Base has to move:");
  Serial.print(base_dest);
  Serial.print(" steps \n");
  
  double shoulder_diff = shoulder_dest - shoulder_degree;
  double shoulder_steps = (shoulder_diff/degreesPerStep);
  Serial.print("Shoulder has to move:");
  Serial.print(shoulder_steps);
  Serial.print(" steps\n");
  
  double elbow_diff = elbow_dest - elbow_degree;
  double elbow_steps = (elbow_diff/degreesPerStep);
  Serial.print("elbow has to move:");
  Serial.print(elbow_steps);
  Serial.print(" steps \n");
  
  double wrist_diff = wrist_dest - wrist_degree;
  double wrist_steps = (wrist_diff/degreesPerStep);
  Serial.print("Wrist has to move:");
  Serial.print(wrist_steps);
  Serial.print(" steps\n");
  
  //set to true when motors have reached target
  boolean target_reached = false;
  
  //move limbs to desired location
  while(!target_reached)
    {                             
      for(i=0; i<4; i++)
      {
        switch(i)
        {
          //positioning of base
          case 0:
            if (base_steps < 0) //object ahead of destination
            {
              base_steps = abs(base_steps);
              Serial.println("Moving base");
              base_offset-=base_steps*degreesPerStep;
              stepBackward(M_base, &base_steps);
              Serial.println("Base now at");
              Serial.print(base_offset);
              Serial.print(" degrees\n");
              break;
            }
            else if(base_steps > 0) //object behind destination
            {
              Serial.println("Moving base");
              base_offset+=base_steps*degreesPerStep;
              stepForward(M_base, &base_steps);
              Serial.println("Base now at");
              Serial.print(base_offset);
              Serial.print(" degrees\n");
              break;
            }
              
          case 1:
            if(elbow_steps > 0)
            {
              Serial.println("Moving elbow forward");
              elbow_degree+=elbow_steps*degreesPerStep;
              stepForward(M_elbow, &elbow_steps);
              Serial.println("elbow now at");
              Serial.print(elbow_degree);
              Serial.print("degrees\n");
              break;
            }
            else if(elbow_steps < 0)
            {
              elbow_steps = abs(elbow_steps);
              Serial.println("Moving elbow backward");
              elbow_degree-=elbow_steps*degreesPerStep;
              stepBackward(M_elbow, &elbow_steps);
              Serial.println("elbow now at");
              Serial.print(elbow_degree);
              Serial.print(" degrees\n");
              break;
            }
              
          case 2:
            if(wrist_steps > 0)
            {
              Serial.println("Moving wrist forward");
              wrist_degree+=wrist_steps*degreesPerStep;
              stepForward(M_wrist, &wrist_steps);
              Serial.println("Wrist now at");
              Serial.print(wrist_degree);
              Serial.print(" more steps away\n");
              break;
            }
            else if(wrist_steps < 0)
            {
              wrist_steps = abs(wrist_steps);
              Serial.println("Moving wrist backward");
              wrist_degree-=wrist_steps*degreesPerStep;
              stepBackward(M_wrist, &wrist_steps);
              Serial.println("Wrist now at");
              Serial.print(wrist_degree);
              Serial.print(" more steps away\n");
              break;
            }
            
          case 3:
            if(shoulder_steps > 0)
            {
              Serial.println("Moving shoulder forward");
              shoulder_degree+=shoulder_steps*degreesPerStep;
              stepForward(M_shoulder, &shoulder_steps);
              Serial.println("Shoulder now at");
              Serial.print(shoulder_degree);
              Serial.print(" degrees\n");
              break;
            }
            else if(shoulder_steps < 0)
            {
              shoulder_steps = abs(shoulder_steps);
              Serial.println("Moving shoulder backward");
              shoulder_degree-=shoulder_steps*degreesPerStep;
              stepBackward(M_shoulder, &shoulder_steps);
              Serial.println("Shoulder now at");
              Serial.print(shoulder_degree);
              Serial.print(" degrees\n");
              break;
            }
        }//end of case statement
        
      }//end of for loop
      if (!(round(shoulder_steps)) && (!round(elbow_steps)) &&
                             (!round(wrist_steps)) &&
                             (!round(base_steps)))
      {
        target_reached = true;
      }
    }//end of infinite while loop
}//end of void loop()

void grabWaitDrop()
{
     //partially closes claw to grab item
     Serial.println("Closing claw");
     closeClaw();
     double wrist_steps=1;
     stepBackward(M_wrist, &wrist_steps);
     wrist_degree-=wrist_steps*degreesPerStep;
     double elbow_steps=2;
     stepBackward(M_elbow, &elbow_steps);
     elbow_degree-=elbow_steps*degreesPerStep;
     Serial.println("Waiting to drop");
     if (rosOn) while(kobukiLocation != "dropoff") {} //wait for drop flag if ros enabled
     else
     {
     while(!Serial.available()) continue;
     String resume_flag = Serial.readString();
     }
     //when resumed open claw to drop item
     elbow_steps=1;
     stepForward(M_elbow, &elbow_steps);
     elbow_degree+=degreesPerStep;
     wrist_steps=1;
     stepForward(M_wrist, &wrist_steps);
     wrist_degree+=degreesPerStep;
     openClaw();
     double shoulder_steps=1;
     stepBackward(M_shoulder, &shoulder_steps);
     shoulder_degree-=degreesPerStep;
}

void stepForward(Stepper myStepper, double *n)
{

  //1 step = 11.125 degree movment or 1/8 circle
  Serial.println("stepping forward");
  myStepper.step(abs((*n))*stepsPerRevolution);
  (*n)=0;
  delay(500);
}

void stepBackward(Stepper myStepper, double *n)
{
  //1 step = 11.125 degree movment or 1/8 circle
  Serial.println("stepping back");
  myStepper.step(-abs((*n))*stepsPerRevolution);
  (*n)=0;
  delay(500);
}

void startCalibration()
{
  String ans;
  int input;
  
  Serial.println("Would you like to calibrate first?");
  while(!Serial.available()) {}
  ans = Serial.readString();
  
  if(ans == "yes")
    {
      Serial.println("What is the degree of the base?");
      while(!Serial.available()) {}
      base_offset = Serial.parseInt();
      
      Serial.println("What is the degree of the shoulder?");
      while(!Serial.available()) {}
      shoulder_degree = Serial.parseInt();

      Serial.println("What is the degree of the elbow?");
      while(!Serial.available()) {}
      elbow_degree = Serial.parseInt();
 
      Serial.println("What is the degree of the wrist?");
      while(!Serial.available()) {}
      wrist_degree = -Serial.parseInt();

      
      //after calibration shoulder, elbow and wrist will be at 90 degrees and base will be at 0
      Serial.println("Calibrating shoulder");
      armCalibration(M_shoulder, &shoulder_degree, shoulder_default);
      Serial.println("Calibrating elbow");
      armCalibration(M_elbow, &elbow_degree, elbow_default);
      Serial.println("Calibrating wrist");
      armCalibration(M_wrist, &wrist_degree, wrist_default);
      Serial.println("Opening Claw");
      openClaw();
      Serial.println("Calibration Complete");
    }
    else
    {
      Serial.println("Setting Defaults");
      base_offset = base_default;
      shoulder_degree = shoulder_default;
      elbow_degree = elbow_default;
      wrist_degree = wrist_default;
      Serial.println("Opening Claw");
      openClaw();
      Serial.println("Calibration Complete");
    }
}

void armCalibration(Stepper motor, double *pos, int default_value)
{
  
  int diff = default_value - *pos;
  double steps = (diff/degreesPerStep);
  Serial.println("moving from");
  Serial.print(*pos);
  Serial.println("\n");
  
  while(round(steps))
  {
    if(steps < 0)
    {
      stepBackward(motor, &steps);
      (*pos)-=steps*degreesPerStep;
    }
    else if(steps > 0)
    {
      stepForward(motor, &steps);
      (*pos)+=steps*degreesPerStep;
    }    
    Serial.println("position is now");
    Serial.println(*pos);
  }
}
