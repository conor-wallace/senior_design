#!/usr/bin/env python
import rospy
import sys
from std_msgs.msg import String

def talker(requested_object):
    pub = rospy.Publisher('chatter', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        object_str = requested_object
        pub.publish(object_str)
        rate.sleep()

if __name__ == '__main__':
    requested_object = str(sys.argv[1])
    try:
        talker(requested_object)
    except rospy.ROSInterruptException:
        pass
