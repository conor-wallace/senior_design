#!/usr/bin/env python
import rospy
from std_msgs.msg import Float64, Float32, String
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
#distance at which manual control takes over
max_distance = 0.35
manual_control = False
t_remaining = 0
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
atTarget = "pickup"
atDropoff = "dropoff"
atGoal = ""
kobuki_position = ""
heading_threshold = 2
headingThresholdPassed = False
#distance_to_goal = 0.0
time = 0
ready = ""
dropTrue = False

def center_callback(center_msg):
   global center, heading_threshold, headingThresholdPassed
   if(headingThresholdPassed == True):
       if(math.abs(center_msg.data) < heading_threshold):
           center = center_msg.data
       else:
           pass
   else:
       if(math.abs(center_msg.data) < heading_threshold):
           headingThresholdPassed = True
           center = center_msg.data
           print("Heading Threshold Passed")
       else:
           center = center_msg.data
   print "center_comp : ", center
   #print "Center Measured : ", center_msg.data

def distance_callback(distance_msg):
   global distance, max_distance, manual_control
   if(manual_control == True):
      pass
   else:
      if(math.isnan(float(distance_msg.data))):
         pass
      else:
         distance = distance_msg.data
         if(distance < max_distance):
            manual_control = True
            distance = max_distance
         print "Distance : " , distance
         print "Auto Control : " , manual_control

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

#def target_callback(target_msg):
#   global atTarget
#   atTarget = "dropoff"

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
bin_sub = rospy.Subscriber("/arm", String, bin_callback)

pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=10, tcp_nodelay=True)
target_pub = rospy.Publisher("/kobuki_location", String, queue_size=10)
armAnglePub = rospy.Publisher("/arm_angle", String, queue_size=10)

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
   global armI
   global armJ
   global armK
   armI = 0
   armJ = 0
   armK = 0
   angle_diff = 0.0
   angle_diff = Kp_angle*(desired_angle - current_angle)
   dist_diff = desired_distance * 0.5
   inc_x = goal.x - x
   inc_y = goal.y - y
   angle_to_goal = atan2(inc_y, inc_x)
   #print "dA: %f, cA: %f, eA: %f, dD: %f, cD: %f, eD: %f" % (desired_angle, current_angle, desired_angle - current_angle, desired_distance, current_distance, desired_distance - current_distance)
   twist_msg = Twist()
   kobuki_msg = String()
   arm_msg = String()

   arm_msg.data = str(center)

   #manual_control = True
   print "Distance : ", distance
   print "Manual Control: ", manual_control

   if(manual_control == True):
      #distance_to_goal = distance - 0.18
      #t = distance_to_goal/0.1
      #print "time", t_remaining
      #time = 0
      print "time", time
      if  time < 15:
         twist_msg.linear.x = 0.1
         twist_msg.angular.z = 0.0
         time += 1
         print "Time Remain", t_remaining
      else:
         twist_msg.linear.x = 0.0
         twist_msg.angular.z = 0.0
         kobuki_msg.data = "pickup"
         ready = "now"
	 #manual_control = False
   else:
      if(stop == "go"):
	twist_msg.linear.x = 0.1

	if(center == 0):
	   twist_msg.angular.z = 0
	else:
	   t = distance/0.1
	   v = math.radians(center)/t
	   twist_msg.angular.z = v
      elif(angle == 45):
	#turns 45 degrees to avoid obstacle
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
      elif(angle == -45):
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

   if(armProcessing == "finished grabbing" and armK < 18 and dropTrue == False):
      while armI < 143:
         twist_msg.linear.x = 0
         twist_msg.angular.z = 0.314
         armI += 1
         pub.publish(twist_msg)
         rate.sleep()
      while armJ < 143:
         twist_msg.linear.x = 0.1
         twist_msg.angular.z = 0
         armJ += 1
         pub.publish(twist_msg)
         rate.sleep()
      while armK < 18:
	 if(armK == 17):
	    dropTrue = True
         twist_msg.linear.x = 0.0
         twist_msg.angular.z = 0
         armK += 1
         pub.publish(twist_msg)
         rate.sleep()
   if(armProcessing == "finished grabbing" and dropTrue == True):
      print("in loop")
      twist_msg.linear.x = 0.0
      twist_msg.angular.z = 0.0
      kobuki_msg.data = "dropoff"

   #print "controlled output to turn: ", twist_msg.angular.z
   #print "Angle Compensation : " , twist_msg.angular.z
   print "Moving Speed : " , twist_msg.linear.x

   target_pub.publish(kobuki_msg)
   pub.publish(twist_msg)
   armAnglePub.publish(arm_msg)
   rate.sleep()
   #rospy.spinOnce()
