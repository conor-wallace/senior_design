#!/usr/bin/env python
import rospy
from std_msgs.msg import Float64, Float32
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
import tf
import numpy
import math
from tf.transformations import euler_from_quaternion

center = 0.0

def center_callback(center_msg):
   global center
   center = center_msg.data
   print "center_comp : ", center
   print "Center Measuered : ", center_msg.data

def distance_callback(distance_msg):
   global distance
   distance = distance_msg.data
   print "Distance : " , distance_msg.data


rospy.init_node('sixwheelcontroller')

center_sub = rospy.Subscriber("/center_image", Float32, center_callback)
distance_sub = rospy.Subscriber("distance", Float32, distance_callback) 

pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=1)

rate = rospy.Rate(10)

while not rospy.is_shutdown():
   twist_msg = Twist()

   if(center == 0):
      twist_msg.angular.z = 0
   else:
      twist_msg.angular.z = center/50
   print "Angle Compensation : " , twist_msg.angular.z

   if(distance > 0.2):
      twist_msg.linear.x = 0.1
   else:
      twist_msg.linear.x = 0.0

   pub.publish(twist_msg)
   rate.sleep()
   #rospy.spinOnce()
