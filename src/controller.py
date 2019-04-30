#!/usr/bin/env python
import rospy
from std_msgs.msg import Int8, Float64, Float32, String
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist, Point
import tf
import numpy
import math
from tf.transformations import euler_from_quaternion
from nav_msgs.msg import Odometry
from math import atan2

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
x = 0.0
y = 0.0 
theta = 0.0
threshold = 0.1
armProcessing = ""
atTarget = 0
atDropoff = 1
wait = 2

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

def newOdom(msg):
   global x
   global y
   global theta
 
   x = msg.pose.pose.position.x
   y = msg.pose.pose.position.y
 
   rot_q = msg.pose.pose.orientation
   (roll, pitch, theta) = euler_from_quaternion([rot_q.x, rot_q.y, rot_q.z, rot_q.w])

def target_callback(target_msg):
   global atTarget
   atTarget = "dropoff"

def bin_callback(bin_msg):
   global armProcessing
   armProcessing = bin_msg.data

rospy.init_node('sixwheelcontroller')

center_sub = rospy.Subscriber("/center_image", Float32, center_callback)
distance_sub = rospy.Subscriber("distance", Float32, distance_callback) 
stop_sub = rospy.Subscriber("stop", String, stop_callback)
turn_sub = rospy.Subscriber("/turn_amount", Float64, turn_callback)
move_sub = rospy.Subscriber("/move_amount", Float64, move_callback)
odom_sub = rospy.Subscriber("/odom", Odometry, newOdom)
bin_sub = rospy.Subscriber("/chatter", String, bin_callback)

pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=1)
target_pub = rospy.Publisher("/kobuki_location", Int8, queue_size=1)

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
goal = Point()
goal.x = 0.0  # GOAL FOR KOBUKI 
goal.y = 0.0
rate = rospy.Rate(10)

while not rospy.is_shutdown():
   angle_diff = 0.0
   angle_diff = Kp_angle*(desired_angle - current_angle)
   dist_diff = desired_distance * 0.5
   inc_x = goal.x - x
   inc_y = goal.y - y
   angle_to_goal = atan2(inc_y, inc_x)
   print "dA: %f, cA: %f, eA: %f, dD: %f, cD: %f, eD: %f" % (desired_angle, current_angle, desired_angle - current_angle, desired_distance, current_distance, desired_distance - current_distance)
   twist_msg = Twist()

   if(distance > 0.2 and stop == "go"):
      twist_msg.linear.x = 0.1
      target_pub.publish(wait)

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
   elif(distance > 0.2 and angle == 45):
      #turns 45 degrees to avoid obstacle
      target_pub.publish(wait)
      i = 0
      while i < 18:
         twist_msg.linear.x = 0
         twist_msg.angular.z = 0.785
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
     #drive to safe zone
      i = 0
      while i < 50:
         twist_msg.linear.x = 0.1
         twist_msg.angular.z = 0.0
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
     #turn back
      i = 0
      while i < 20:
         twist_msg.linear.x = 0
         twist_msg.angular.z = -0.785
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
   elif(distance > 0.2 and angle == -45):
      #turns 45 degrees to avoid obstacle
      i = 0
      while i < 18:
         twist_msg.linear.x = 0
         twist_msg.angular.z = -0.785
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
     #drive to safe zone
      i = 0
      while i < 50:
         twist_msg.linear.x = 0.1
         twist_msg.angular.z = 0.0
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
     #turn back
      i = 0
      while i < 20:
         twist_msg.linear.x = 0
         twist_msg.angular.z = 0.785
         i += 1
         pub.publish(twist_msg)
         rate.sleep()
   else:
      twist_msg.linear.x = 0.0
      twist_msg.angular.z = 0.0

   #Wait for arm to pick up object
   if(0.1 < distance < 0.2):
      target_pub.publish(atTarget)

   #Drive back to original position
   if(armProcessing == "object"):
      target_pub.publish(wait)
      if abs(angle_to_goal - theta) > 0.1:
         twist_msg.linear.x = 0.0
         twist_msg.angular.z = 0.3
      elif (abs(inc_x) < threshold and abs(inc_y) < threshold):
         twist_msg.linear.x = 0.0
         twist_msg.angular.z = 0.0
      else:
         twist_msg.linear.x = 0.1
         twist_msg.angular.z = 0.0

   #Reached the bin
   if(twist_msg.linear.x == 0.0 and twist_msg.angular.z == 0.0):
      target_pub.publish(atDropoff)


   print "controlled output to turn: ", twist_msg.angular.z

   print "Angle Compensation : " , twist_msg.angular.z
   print "Moving Speed : " , twist_msg.linear.x

   pub.publish(twist_msg)
   rate.sleep()
   #rospy.spinOnce()
