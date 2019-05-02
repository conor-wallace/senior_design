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
double ServoPos;

//universal index
int i;

//universal status log variable
char* log_msg;
char temp_val[8];

//These defines will stand the arm straigt up and wrist at 45 degrees as a default
//degrees are measured from positive y-axis
#define shoulder_default  0
#define elbow_default     0
#define wrist_default     0
#define base_default      0

//ros istantiations and variables
ros::NodeHandle  nh;
String kobukiLocation;
String armStatus;
double reach_dist = 0; //how far away the obj is from the camera
double err_offset = 0; //how far the object is from the center of camera
boolean pickup_complete = false;
boolean dropoff_complete = false;

void kobukiCb( const std_msgs::String& msg){
  kobukiLocation = msg.data;
}


void distanceCb( const std_msgs::Float32& msg){
  reach_dist = msg.data;
}

void centerCb( const std_msgs::Float32& msg){
  err_offset = msg.data;
}

std_msgs::String str_msg;
ros::Subscriber<std_msgs::String> sub1("kobuki_location", kobukiCb );
ros::Subscriber<std_msgs::Float32> sub2("distance", distanceCb );
ros::Subscriber<std_msgs::Float32> sub3("center_image", centerCb );
ros::Publisher chatter("chatter", &str_msg);


void setup()
{
  //motor setup
  M_claw.attach(3);
  M_base.setSpeed(60);
  M_shoulder.setSpeed(60);
  M_elbow.setSpeed(60);
  M_wrist.setSpeed(60);
  M_elbowWrist.setSpeed(60);
  nh.getHardware()->setBaud(57600);
 
  //ros setup
  nh.initNode();
  nh.advertise(chatter);
  nh.subscribe(sub1);
  nh.subscribe(sub2);
  nh.subscribe(sub3);
}

void loop()
{
  //nh.spinOnce();
  nh.loginfo("Wating to for input...");
  if(kobukiLocation == "dropoff" && !pickup_complete)
  {
    nh.loginfo("Centering base");
    center(err_offset);
    
    nh.loginfo("Moving to prep degree");
    moveToDegree(0,45,90,-45);
    
    //nh.loginfo("Reaching for object");
    //reach(0);
    
    nh.loginfo("Grabbing Object");
    grabWait();
    nh.loginfo("Finished grabbing");
    pickup_complete = true;
    str_msg.data = "Finished grabbing";
    chatter.publish( &str_msg );
    nh.spinOnce();
  }
  if (kobukiLocation == "dropoff" && !dropoff_complete)
  {
    nh.loginfo("Dropping Object");
    Drop();
    str_msg.data = "Finished dropping";
    chatter.publish( &str_msg );
    nh.loginfo("Resetting");
    armReset();
    dropoff_complete = true;
    nh.spinOnce();
  }
  nh.spinOnce();
  delay(100);
}

void center(double offset)
{
  double base_steps = offset/(2*degreesPerStep);
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

void reach(double dist)
{

  while(int(dist) > 0)
  {
    
    double shoulder_steps=2;
    double dual_step = 1;
    //double elbow_steps=1;
    //double wrist_steps=1;
    stepBackward(M_shoulder, &shoulder_steps);
    shoulder_degree-=shoulder_steps*degreesPerStep;
    stepForward(M_elbowWrist, &dual_step);
    //stepForward(M_wrist, &wrist_steps);
    wrist_degree-=dual_step*degreesPerStep;
    //stepForward(M_elbow, &elbow_steps)gree+=elbow_steps*degr;
    elbow_degree+=dual_step*degreesPerStep;
    dist--;
    
    //dtostrf(shoulder_degree, 6, 2, temp_val);
    //sprintf(log_msg, "Shoulder now at %d degrees", temp_val);
   // nh.loginfo(log_msg);
    
    //dtostrf(elbow_degree, 6, 2, temp_val);
    //sprintf(log_msg, "Elbow now at %d degrees", temp_val);
   // nh.loginfo(log_msg);
    
    //dtostrf(wrist_degree, 6, 2, temp_val);
    //sprintf(log_msg, "Wrist now at %d degrees", temp_val);
   // nh.loginfo(log_msg);
  }
  nh.spinOnce();
}

void armReset()
{
  moveToDegree(base_default, shoulder_default, elbow_default, wrist_default);
}

void closeClaw()
{
  //for(i = 0; i < 160; i += 1)  // goes from 0 degrees to 180 degrees 
 //{                                  // in steps of 1 degree 
    M_claw.write(i);    // tell servo to go to position in variable 'pos' 
    nh.spinOnce(); 
    delay(100);                       // waits 15ms for the servo to reach the position 
  //} 
}

void openClaw()
{
    //for(i = 5; i>=1; i-=1)     // goes from 180 degrees to 0 degrees 
  //{                                
    M_claw.write(i);              // tell servo to go to position in variable 'pos' 
    nh.spinOnce(); 
    delay(100);                        // waits 15ms for the servo to reach the position 
  //}
}

void moveToDegree(double base_dest, double shoulder_dest, double elbow_dest, double wrist_dest)
{
  
  //gather location destinations in degrees    && 
  //calculation of the distance need to travel
  nh.loginfo("Calculating base offset");
  double base_diff = base_dest - base_offset;
  double base_steps = (base_diff/degreesPerStep);
  ////dtostrf(base_steps, 6, 2, temp_val);
  ////sprintf(log_msg, "Base has to move %d steps.", temp_val);
  //nh.loginfo(log_msg);
  
  nh.loginfo("Calculating shoulder offset");
  double shoulder_diff = shoulder_dest - shoulder_degree;
  double shoulder_steps = (shoulder_diff/degreesPerStep);
  ////dtostrf(shoulder_steps, 6, 2, temp_val);
  ////sprintf(log_msg, "Shoulder has to move %d steps.", temp_val);
  //nh.loginfo(log_msg);
  
  nh.loginfo("Calculating elbow offset");
  double elbow_diff = elbow_dest - elbow_degree;
  double elbow_steps = (elbow_diff/degreesPerStep);
  ////dtostrf(elbow_steps, 6, 2, temp_val);
  ////sprintf(log_msg, "Elbow has to move %d steps.", temp_val);
  //nh.loginfo(log_msg);
  
  nh.loginfo("Calculating wrist offset");
  double wrist_diff = wrist_dest - wrist_degree;
  double wrist_steps = (wrist_diff/degreesPerStep);
  ////dtostrf(wrist_steps, 6, 2, temp_val);
  ////sprintf(log_msg, "Wrist has to move %d steps.", temp_val);
  //nh.loginfo(log_msg);
  
  //set to true when motors have reached target
  boolean target_reached = false;
  
  //move limbs to desired location
  if(!target_reached)
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
              
              nh.loginfo("Moving base");
              base_offset-=base_steps*degreesPerStep;
              stepBackward(M_base, &base_steps);
              
              ////dtostrf(base_offset, 6, 2, temp_val);
              ////sprintf(log_msg, "Base now at %d degrees.", temp_val);
              //nh.loginfo(log_msg);
              break;
            }
            else if(base_steps > 0) //object behind destination
            {
              nh.loginfo("Moving base");
              base_offset+=base_steps*degreesPerStep;
              stepForward(M_base, &base_steps);
              
              ////dtostrf(base_offset, 6, 2, temp_val);
              ////sprintf(log_msg, "Base now at %d degrees.", temp_val);
              //nh.loginfo(log_msg);
              break;
            }
              
          case 1:
            if(elbow_steps > 0)
            {
              nh.loginfo("Moving elbow forward");
              elbow_degree+=elbow_steps*degreesPerStep;
              stepForward(M_elbow, &elbow_steps);
              
              ////dtostrf(elbow_degree, 6, 2, temp_val);
              ////sprintf(log_msg, "Elbow now at %d degrees.", temp_val);
              //nh.loginfo(log_msg);
              break;
            }
            else if(elbow_steps < 0)
            {
              elbow_steps = abs(elbow_steps);
              nh.loginfo("Moving elbow backward");
              elbow_degree-=elbow_steps*degreesPerStep;
              stepBackward(M_elbow, &elbow_steps);
              
              //dtostrf(elbow_degree, 6, 2, temp_val);
              //sprintf(log_msg, "Elbow now at %d degrees.", temp_val);
             // nh.loginfo(log_msg);
              break;
            }
              
          case 2:
            if(wrist_steps > 0)
            {
              nh.loginfo("Moving wrist forward");
              wrist_degree+=wrist_steps*degreesPerStep;
              stepForward(M_wrist, &wrist_steps);
              
              ////dtostrf(wrist_degree, 6, 2, temp_val);
              //sprintf(log_msg, "Wrist now at %d degrees.", temp_val);
             // nh.loginfo(log_msg);
              break;
            }
            else if(wrist_steps < 0)
            {
              wrist_steps = abs(wrist_steps);
              nh.loginfo("Moving wrist backward");
              wrist_degree-=wrist_steps*degreesPerStep;
              stepBackward(M_wrist, &wrist_steps);
              
              //dtostrf(wrist_degree, 6, 2, temp_val);
              //sprintf(log_msg, "Wrist now at %d degrees.", temp_val);
             // nh.loginfo(log_msg);
              break;
            }
            
          case 3:
            if(shoulder_steps > 0)
            {
              nh.loginfo("Moving shoulder forward");
              shoulder_degree+=shoulder_steps*degreesPerStep;
              stepForward(M_shoulder, &shoulder_steps);
              
              //dtostrf(shoulder_degree, 6, 2, temp_val);
              //sprintf(log_msg, "Shoulder now at %d degrees.", temp_val);
             // nh.loginfo(log_msg);
              break;
            }
            else if(shoulder_steps < 0)
            {
              shoulder_steps = abs(shoulder_steps);
              nh.loginfo("Moving shoulder backward");
              shoulder_degree-=shoulder_steps*degreesPerStep;
              stepBackward(M_shoulder, &shoulder_steps);
              
              //dtostrf(shoulder_degree, 6, 2, temp_val);
              //sprintf(log_msg, "Shoulder now at %d degrees.", temp_val);
             // nh.loginfo(log_msg);
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
    nh.spinOnce(); 
    delay(100);
}//end of void loop()

void grabWait()
{
   //partially closes claw to grab item
   nh.loginfo("Closing claw");
   closeClaw();
   delay(700);
   double wrist_steps=1;
   stepBackward(M_wrist, &wrist_steps);
   wrist_degree-=degreesPerStep;
   double elbow_steps=1;
   stepBackward(M_elbow, &elbow_steps);
   elbow_degree-=degreesPerStep;
   nh.loginfo("Waiting to drop");
   nh.spinOnce(); 
   delay(100);   
}

void Drop()
{
   nh.loginfo("dropping object");
   double elbow_steps=1;
   stepForward(M_elbow, &elbow_steps);
   elbow_degree+=degreesPerStep;
   double wrist_steps=1;
   stepForward(M_wrist, &wrist_steps);
   wrist_degree+=degreesPerStep;
   openClaw();
   delay(100);
   double shoulder_steps=1;
   stepBackward(M_shoulder, &shoulder_steps);
   shoulder_degree-=degreesPerStep;
   nh.spinOnce(); 
   delay(100); 
}

void stepForward(Stepper myStepper, double *n)
{

  //1 step = 11.125 degree movment or 1/8 circle
  nh.loginfo("stepping forward");
  myStepper.step(abs((*n))*stepsPerRevolution);
  (*n)=0;
  delay(100);
}

void stepBackward(Stepper myStepper, double *n)
{
  //1 step = 11.125 degree movment or 1/8 circle
  nh.loginfo("stepping back");
  myStepper.step(-abs((*n))*stepsPerRevolution);
  (*n)=0;
  delay(100);
}

void armCalibration(Stepper motor, double *pos, int default_value)
{
  
  int diff = default_value - *pos;
  double steps = (diff/degreesPerStep);
              

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
             
  }
}

