#!/usr/bin/env python
import rospy
import std_msgs
from std_msgs.msg import Float32, String

rospy.init_node('pub_test', anonymous=True)
distPub = rospy.Publisher('distance', Float32, queue_size=10)
kobukiPub = rospy.Publisher('kobuki_location', String, queue_size=10)
compPub = rospy.Publisher('center_image', Float32, queue_size=10)
rate = rospy.Rate(10)
rate.sleep()

while not rospy.is_shutdown():
   distPub.publish(0.18)
   kobukiPub.publish("pickup")
   compPub.publish(25.0)
   rate.sleep()
