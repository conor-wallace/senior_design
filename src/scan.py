#!/usr/bin/env python
import rospy
from std_msgs.msg import Float64
#from sensor_msgs.msg import image
from sensor_msgs.msg import LaserScan
from message_filters import ApproximateTimeSynchronizer, Subscriber

#image_sub = Subscriber("/detection_image", Image)
pub = rospy.Publisher('/mod_scan', LaserScan, queue_size=10)

turn_pub = rospy.Publisher('/turn_amount', Float64, queue_size=1)
move_pub = rospy.Publisher('/move_amount', Float64, queue_size=1)
busy_counter = 0
def callback(scan_l1_msg, scan_l2_msg, scan_l3_msg, scan_l4_msg, scan_l5_msg, scan_r5_msg, scan_r4_msg, scan_r3_msg, scan_r2_msg, scan_r1_msg):
        global busy_counter
        if busy_counter > 0:
           busy_counter = busy_counter - 1
           return

        print "in callback"
        #num_values_to_look_at = 160
        #mod_msg = LaserScan()
        #mod_msg.ranges = [len_ranges/2-1-num_values_to_look_at/2:len_ranges/2+num_values_to_look_at/2]
        #mod_msg.angle_increment = msg.angle_increment
        #mod_msg.time_increment = msg.time_increment
        #mod_msg.range_min = msg.range_min
        #mod_msg.range_max = msg.range_max
        FRONT_SAFE_RANGE = 0.4
        turn_amount =Float64(0.0)        
        move_amount =Float64(0.0)
        if (min(scan_l1_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_r1_msg.ranges) > FRONT_SAFE_RANGE):
                print "Move forward"
                move_amount.data = 0.5
                turn_amount.data = 0.0
                print move_amount
        else:
                if (min(scan_r1_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_r2_msg.ranges) > FRONT_SAFE_RANGE):
                        print "Turn...36 to right"
                        turn_amount.data = -45
                        busy_counter = 40
                elif (min(scan_l1_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_l2_msg.ranges) > FRONT_SAFE_RANGE):
                        print "Turn...36 to left"
                        turn_amount.data = 45
                        busy_counter = 40
                elif (min(scan_r2_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_r3_msg.ranges) > FRONT_SAFE_RANGE):
                        print "Turn...72 to right"
                        turn_amount.data = -90
                        busy_counter = 80
                elif (min(scan_l2_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_l3_msg.ranges) > FRONT_SAFE_RANGE):
                        print "Turn...72 to left"
                        turn_amount.data = 90
                        busy_counter = 80

                elif (min(scan_r3_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_r4_msg.ranges) > FRONT_SAFE_RANGE):
                        print "Turn...108 to right"
                        turn_amount.data = -135
                        busy_counter = 120
                elif (min(scan_l3_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_l4_msg.ranges) > FRONT_SAFE_RANGE):
                        print "Turn...108 to left"
                        turn_amount.data = 135
                        busy_counter = 120
                
                else:
                        print "Move backward"
                        move_amount.data = -0.5
                        turn_amount.data = 0.0
                        busy_counter = 5
                #if (min(scan_l5_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_r5_msg.ranges) > FRONT_SAFE_RANGE):
                #else:
                #        turn_amount.data = 0.0

                #elif (min(scan_r4_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_r5_msg.ranges) > FRONT_SAFE_RANGE):
                #        print "Turn...144 to right"
                #        turn_amount.data = 144
                #        busy_counter = 80
                #elif (min(scan_l4_msg.ranges) > FRONT_SAFE_RANGE) and (min(scan_l5_msg.ranges) > FRONT_SAFE_RANGE):
                #        print "Turn...144 to left"
                #       turn_amount.data = -144
                #        busy_counter = 80
                
        print turn_amount.data
        print move_amount.data
        if turn_amount.data != -1000:
           turn_pub.publish(turn_amount)
        if move_amount.data != -1000:
           move_pub.publish(move_amount)

rospy.init_node('scan')

print "defining subs"
scan_l1_sub = Subscriber("/scan_l1", LaserScan)
scan_l2_sub = Subscriber("/scan_l2", LaserScan)
scan_l3_sub = Subscriber("/scan_l3", LaserScan)
scan_l4_sub = Subscriber("/scan_l4", LaserScan)
scan_l5_sub = Subscriber("/scan_l5", LaserScan)
scan_r5_sub = Subscriber("/scan_r5", LaserScan)
scan_r4_sub = Subscriber("/scan_r4", LaserScan)
scan_r3_sub = Subscriber("/scan_r3", LaserScan)
scan_r2_sub = Subscriber("/scan_r2", LaserScan)
scan_r1_sub = Subscriber("/scan_r1", LaserScan)

print "defining ats"


ats = ApproximateTimeSynchronizer([scan_l1_sub, scan_l2_sub, scan_l3_sub, scan_l4_sub, scan_l5_sub, scan_r5_sub, scan_r4_sub, scan_r3_sub, scan_r2_sub, scan_r1_sub], queue_size=5, slop=1.0)
print "before register callback"
ats.registerCallback(callback)

#sub = rospy.Subscriber('/scan', LaserScan, callback)
rospy.spin()
