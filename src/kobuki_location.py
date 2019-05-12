#!/usr/bin/env python
import sys
import rospy
import std_msgs
from std_msgs.msg import Float32, String

rospy.init_node('pub_test', anonymous=True)
kobukiPub = rospy.Publisher("kobuki_location", String, queue_size=10)
rate = rospy.Rate(10)
rate.sleep()

while not rospy.is_shutdown():
   kobukiPub.publish(str(sys.argv[1]))
rate.sleep()
