#!/usr/bin/env python
import rospy
from std_msgs.msg import Float64, Float32, String
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
import tf
import numpy
import math
from tf.transformations import euler_from_quaternion

# NEW CODe
center = 0.0
distance = 0.0
stop = ''
desired_angle = 0.0
desired_distance = 0.0
current_angle = 0.0
current_distance = 0.0 
center = 0.0 
angle = 0.0
auto = []


def center_callback(center_msg):
   global center
   center = center_msg.data
   print "center_comp : ", center
   #print "Center Measured : ", center_msg.data

def distance_callback(distance_msg):
   global distance
   distance = distance_msg.data
   #print "Distance : " , distance_msg.data

def stop_callback(stop_msg):
   global stop
   stop = stop_msg.data

def turn_callback(turn_msg):
   global desired_angle
   global current_angle
   global angle
   desired_angle = current_angle + turn_msg.data*3.1456/180
   angle = turn_msg.data
   #print "desired_angle: ", desired_angle

def move_callback(move_msg):
   global desired_distance
   desired_distance = move_msg.data
   #print "desired_distance: ", desired_distance
      
def imu_callback(imu_msg):
   global current_angle
   xyzw_array = lambda o: numpy.array([o.x, o.y, o.z, o.w])
   euler = tf.transformations.euler_from_quaternion(xyzw_array(imu_msg.orientation))
   current_angle = euler[2] #imu_msg.orientation.x
   #print "current_angle: ", current_angle

def dis_callback(dis_msg):
   global current_distance 
   current_distance = imu_msg.linear.x
   #print "current_dist: ", current_dist

rospy.init_node('sixwheelcontroller')

center_sub = rospy.Subscriber("/center_image", Float32, center_callback)
distance_sub = rospy.Subscriber("distance", Float32, distance_callback) 
#stop_sub = rospy.Subscriber("should_stop", String, stop_callback)
turn_sub = rospy.Subscriber("/turn_amount", Float64, turn_callback)
move_sub = rospy.Subscriber("/move_amount", Float64, move_callback)

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
rate = rospy.Rate(10)

while not rospy.is_shutdown():
   angle_diff = 0.0
   angle_diff = Kp_angle*(desired_angle - current_angle)
   dist_diff = desired_distance * 0.5
   print "dA: %f, cA: %f, eA: %f, dD: %f, cD: %f, eD: %f" % (desired_angle, current_angle, desired_angle - current_angle, desired_distance, current_distance, desired_distance - current_distance)
   twist_msg = Twist()

   if(distance > 0.2):
      twist_msg.linear.x = 0.1

      if(center == 0):                             
         twist_msg.angular.z = 0
      else:
         if(distance > 0.2):
            t = distance/0.1
            v = math.radians(center)/t
            twist_msg.angular.z = v
         else:
            v = math.radians(center)/50
            twist_msg.angular.z = v
   elif(distance > 0.2 and dist_diff < 0.1):
      #turns 45 degrees to avoid obstacle
      i = 0
      while i < 10:
         twist_msg.linear.x = 0
         twist_msg.angular.z = 0.785
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
     #drive to safe zone
      i = 0
      while i < 10:
         twist_msg.linear.x = 0.1
         twist_msg.angular.z = 0.0
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
     #turn back
      i = 0
      while i < 10:
         twist_msg.linear.x = 0
         twist_msg.angular.z = -0.785
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
   else:
      twist_msg.linear.x = 0.0
      twist_msg.angular.z = 0.0

   """
   if(auto == True):
      if(angle_diff == 0):
         twist_msg.angular.z = 0.0
      else:
         twist_msg.angular.z = angle_diff
         if(angle > 0.0):
            twist_msg.linear.x = 0.1
         elif(angle < 0.0):
            twist_msg.linear.x = 0.1
      
         if(angle == 0.0):
            twist_msg.angular.z = angle_diff * -1
   else:
      auto == False
  
   print "Auto = ", bool(auto)

   if(auto == True):
      #if(dist_diff > 0):
      #   twist_msg.linear.x = 0.0
      #elif(dist_diff < 0.0):
      #   twist_msg.linear.x = -0.1
      i = 0
      while i < 10:
        twist_msg.linear.x = 0
        twist_msg.angular.z = 0.785
        i += 1
        pub.publish(twist_msg)
        rate.sleep()

      if(angle_diff == 0):
         twist_msg.angular.z = 0.0
      else:
         i = 0
         twist_msg.angular.z = 0.785
         #if(angle > 0.0):
         #   twist_msg.linear.x = 0.1
         #elif(angle < 0.0):
         #   twist_msg.linear.x = 0.1
      
         #if(angle == 0.0):
         #   twist_msg.angular.z = angle_diff * -1 
   else:
      auto == False
   """
   print "controlled output to turn: ", twist_msg.angular.z

   print "Angle Compensation : " , twist_msg.angular.z
   print "Moving Speed : " , twist_msg.linear.x

   pub.publish(twist_msg)
   rate.sleep()
   #rospy.spinOnce()
