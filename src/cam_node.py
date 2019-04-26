#!/usr/bin/env python
import rospy
import darknet_ros_msgs
import numpy
import math
import sys
import std_msgs
from std_msgs.msg import String, Float32
from darknet_ros_msgs.msg import BoundingBoxes, BoundingBox

requested_object = sys.argv[1]
shouldStop = "go"
compensation = 0.0
x_coordinate = 0.0
y_coordinate = 0.0

def imageCallback(data):
    global compensation, x_coordinate, y_coordinate, requested_object, shouldStop
    object_index = 0
    for i in range(0, len(data.bounding_boxes)):
        if data.bounding_boxes[object_index].Class == requested_object:
            print("Found it!")
	    shouldStop = "go"
            x_coordinate = (data.bounding_boxes[object_index].xmin+data.bounding_boxes[object_index].xmax)/2
            y_coordinate = (data.bounding_boxes[object_index].ymin+data.bounding_boxes[object_index].ymax)/2
            print("X centered: " + str(x_coordinate))
            if x_coordinate > 320:
                x_diff = x_coordinate - 320
                compensation = math.degrees(math.atan((2*x_diff*math.tan(90))/640))
                print("Turn " + str(compensation) + " degrees")
            elif x_coordinate < 320:
                x_diff = 320 - x_coordinate
                compensation = abs(math.degrees(math.atan((2*x_diff*math.tan(90))/640)))
                print("Turn " + str(compensation) + " degrees")
            else:
                print("Perfectly Centered!")
            break
        else:
            compensation = 0.0
	    shouldStop = "stop"
            print("Object not found")
        object_index += 1

def pub_webcam():
    global compensation, x_coordinate, y_coordinate, shouldStop
    rospy.init_node('pub_webcam', anonymous=True)
    objectPub = rospy.Publisher('object', String, queue_size=10)
    centerXPub = rospy.Publisher('center_x', Float32, queue_size=10)
    centerYPub = rospy.Publisher('center_y', Float32, queue_size=10)
    compPub = rospy.Publisher('/center_image', Float32, queue_size=10)
    rospy.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes, imageCallback)
    rate = rospy.Rate(10)
    rate.sleep()
    while not rospy.is_shutdown():
	objectPub.publish(shouldStop)
        centerXPub.publish(x_coordinate)
        centerYPub.publish(y_coordinate)
        compPub.publish(compensation)
        rate.sleep()

if __name__ == '__main__':
    try:
        pub_webcam()
    except rospy.ROSInterruptException:
        pass
