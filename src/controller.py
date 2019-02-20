#!/usr/bin/env python
import rospy
from std_msgs.msg import Float64
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
import tf
import numpy
import math
from tf.transformations import euler_from_quaternion


#scan_pub = rospy.Publisher('/
#imu_pub = rospy.Publisher('/imu', Imu, queue_size=10)
#dis_pub = rospy.Publisher('/imu', Imu, queue_size=10)

desired_angle = 0.0
desired_distance = 0.0
current_angle = 0.0
current_distance = 0.0

def turn_callback(turn_msg):
   global desired_angle
   global current_angle
   desired_angle = current_angle + turn_msg.data*3.1456/180
   print "desired_angle: ", desired_angle

def move_callback(move_msg):
   global desired_distance
   desired_distance = move_msg.data
   print "desired_distance: ", desired_distance
      
def imu_callback(imu_msg):
   global current_angle
   xyzw_array = lambda o: numpy.array([o.x, o.y, o.z, o.w])
   euler = tf.transformations.euler_from_quaternion(xyzw_array(imu_msg.orientation))
   current_angle = euler[2] #imu_msg.orientation.x
   print "current_angle: ", current_angle

def dis_callback(dis_msg):
   global current_distance 
   current_distance = imu_msg.linear.x
   print "current_dist: ", current_dist




rospy.init_node('sixwheelcontroller')

turn_sub = rospy.Subscriber("/turn_amount", Float64, turn_callback)
move_sub = rospy.Subscriber("/move_amount", Float64, move_callback)
#imu_sub = rospy.Subscriber("/imu",         Imu,     imu_callback)
rospy.Subscriber("mobile_base/sensors/imu_data", Imu, imu_callback)

#pub = rospy.Publisher('/cmd_vel_sub', Twist, queue_size=1)
pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=1)
  
def getDirection(x):
  if x > 0:
    return 1
  elif x < 0: 
    return -1
  else:
    return 0

def valmap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


Kp = 0.75
Kp_angle = 2
rate = rospy.Rate(15)
while not rospy.is_shutdown():

   angle_diff = 0.0
   #if desired_angle != 0:
   angle_diff = Kp_angle*(desired_angle - current_angle)#1.0*getDirection(desired_angle)#valmap(abs(desired_angle), 36, 144, 0.8, 1.0)*getDirection(desired_angle)
   dist_diff = desired_distance * 0.5 #- current_distance
   print "dA: %f, cA: %f, eA: %f, dD: %f, cD: %f, eD: %f" % (desired_angle, current_angle, desired_angle - current_angle, desired_distance, current_distance, desired_distance - current_distance)
   twist_msg = Twist()
   
   if(dist_diff == 0):
      twist_msg.linear.x = 0.0
   elif(dist_diff > 0.0):
      print "distance greater than 3.0"
      twist_msg.linear.x = 0.5
   elif(dist_diff < 0.0):
      print "distance less than 1.0"
      twist_msg.linear.x = -0.5
  
   if(angle_diff == 0):
      twist_msg.angular.z = 0.0
   else:
      twist_msg.angular.z = angle_diff
   print "controlled output to turn: ", twist_msg.angular.z

   #elif(angle_diff > 0.785):
   #   print "angle greater than 0.785"
   #   twist_msg.angular.z = 0.5
   #elif(angle_diff < 0):
   #   print "angle less than 0"
   #   twist_msg.angular.z = 0.5

   pub.publish(twist_msg)      
   rate.sleep()
   #rospy.spinOnce()
   
