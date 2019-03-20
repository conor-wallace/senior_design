#!/usr/bin/env python
import rospy
from std_msgs.msg import Float64, Float32, String
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
import tf
import numpy
import math
from tf.transformations import euler_from_quaternion

#new code
center = 0.0
distance = 0.0
stop = ''

def center_callback(center_msg):
   global center
   center = center_msg.data
   print "center_comp : ", center
   print "Center Measured : ", center_msg.data

def distance_callback(distance_msg):
   global distance
   distance = distance_msg.data
   print "Distance : " , distance_msg.data

def stop_callback(stop_msg):
   global stop
   stop = stop_msg.data

rospy.init_node('sixwheelcontroller')

center_sub = rospy.Subscriber("/center_image", Float32, center_callback)
distance_sub = rospy.Subscriber("distance", Float32, distance_callback) 
stop_sub = rospy.Subscriber("should_stop", String, stop_callback)

pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=1)

rate = rospy.Rate(10)

while not rospy.is_shutdown():
   twist_msg = Twist()
   
   if(distance > 0.2):
      linear_vel = 0.1
   else:
      linear_vel = 0.0

   if(stop == "go"):
     twist_msg.linear.x = linear_vel

     if(center == 0):                             
        twist_msg.angular.z = 0
     else:
        if(linear_vel == 0.1):
           t = distance/0.1
           v = math.radians(center)/t
           twist_msg.angular.z = v
        else:
           v = math.radians(center)/50
           twist_msg.angular.z = v
   else:
      twist_msg.linear.x = 0.0
      twist_msg.angular.z = 0.0

   print "Angle Compensation : " , twist_msg.angular.z
   print "Moving Speed : " , twist_msg.linear.x

   pub.publish(twist_msg)
   rate.sleep()
   #rospy.spinOnce()
