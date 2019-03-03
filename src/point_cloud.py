#!/usr/bin/env python
import rospy
import darknet_ros_msgs
import numpy
import math
import std_msgs

distance = 0.0

def pcCallback(data):
    global distance
    #convert image_raw data to pointcloud data
    #take in centroid of the object's pixel area
    #retrieve distance nearest to the centroid
    #distance = pointcloud(x, y)...

def pub_webcam():
    rospy.init_node('pub_distance', anonymous=True)
    distPub = rospy.Publisher('/distance', Float32, queue_size=10)
    rospy.Subscriber('/image/depth/pointcloud', PointCloud, pcCallback)
    rate = rospy.Rate(10)
    rate.sleep()
    while not rospy.is_shutdown():
        distPub.publish(compensation)
        rate.sleep()

if __name__ == '__main__':
    try:
        pub_webcam()
    except rospy.ROSInterruptException:
        pass
