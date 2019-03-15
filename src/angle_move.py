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


rospy.init_node('sixwheelcontroller')

center_sub = rospy.Subscriber("/center_image", Float32, center_callback)

pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=1)

rate = rospy.Rate(10)

while not rospy.is_shutdown():
   twist_msg = Twist()

   if(center == 0):
      twist_msg.angular.z = 0
   else:
      twist_msg.angular.z = center/50
   print "Angle Compensation : " , twist_msg.angular.z

   pub.publish(twist_msg)
   rate.sleep()
   #rospy.spinOnce()
