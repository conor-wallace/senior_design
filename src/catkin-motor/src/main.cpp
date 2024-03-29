#include <ros.h>
#include <mbed.h>
//#include "mbed_events.h"
#include <std_msgs/String.h>
#include <sstream>
//#include "motors.h"


int main() {
int i,j;
ros::init(argc, argv, "talker");
ros::NodeHandle n;
ros::Publisher chatter_pub = n.advertise<std_msgs::String>("chatter", 1000);
ros::Rate loop_rate(10);
//DigitalOut enable(PTD4, 0);//enable bit for indexer?
DigitalOut step(PTA1);
DigitalOut dir(PTA2, 1); //going one dir for test

//Step modes 0,1,2

DigitalOut mode0(PTB0);
DigitalOut mode1(PTB1);
DigitalOut mode2(PTB2);


mode0 = 1;
mode1 = 1;
mode2 = 1;

while(1){
    dir=1;
    for(i=0; i<=10000; i++) {
        step = 0;
        wait(0.0001);
        step = 1;
	std_msgs::String msg;
    	std::stringstream ss;
 	ss << "hello world " << count;
	msg.data = ss.str();
	ROS_INFO("%s", msg.data.c_str());    
    }
    dir=0;
    for(j=0; j<=10000; j++){
        step = 0;
        wait(0.0001);
        step = 1;
    }
}
}
