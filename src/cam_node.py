#!/usr/bin/env python
import rospy
import darknet_ros_msgs
import numpy
import math
import std_msgs
from std_msgs.msg import String, Float32
from darknet_ros_msgs.msg import BoundingBoxes, BoundingBox

object = ''
compensation = 0.0

def imageCallback(data):
    global compensation
    object_index = 0
    for i in range(0, len(data.bounding_boxes)):
        if data.bounding_boxes[object_index].Class == object:
            print("Found it!")
            break
        object_index += 1

    x_centered = (data.bounding_boxes[object_index].xmin+data.bounding_boxes[object_index].xmax)/2
    print("X centered: " + str(x_centered))
    if x_centered > 320:
        x_diff = x_centered - 320
        compensation = math.degrees(math.atan((2*x_diff*math.tan(90))/640))
        print("Turn " + str(compensation) + " degrees")
    elif x_centered < 320:
        x_diff = 320 - x_centered
        compensation = abs(math.degrees(math.atan((2*x_diff*math.tan(90))/640)))
        print("Turn " + str(compensation) + " degrees")
    else:
        print("Perfectly Centered!")

def objectCallback(data):
    global object
    object = data.data

def pub_webcam():
    rospy.init_node('pub_webcam', anonymous=True)
    compPub = rospy.Publisher('/center_image', Float32, queue_size=10)
    rospy.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes, imageCallback)
    rospy.Subscriber('chatter', String, objectCallback)
    rate = rospy.Rate(10)
    rate.sleep()
    while not rospy.is_shutdown():
        compPub.publish(compensation)
        rate.sleep()

if __name__ == '__main__':
    try:
        pub_webcam()
    except rospy.ROSInterruptException:
        pass
