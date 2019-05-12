#include<iostream>
#include <ros/ros.h>
// PCL specific includes
#include <std_msgs/Float32.h>
#include <sensor_msgs/PointCloud2.h>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>

ros::Publisher pub;
ros::Publisher pub2;
//float coordinate[3];
float x_coordinate = 0.0;
float y_coordinate = 0.0;
float angle = 0.0;

void x_callback(const std_msgs::Float32::ConstPtr& x)
{
  x_coordinate = x->data;
}

void y_callback(const std_msgs::Float32::ConstPtr& y)
{
  y_coordinate = y->data;
}

void center_callback(const std_msgs::Float32::ConstPtr& msg)
{
  angle = msg->data;
}

//recieve PointCloud2 data in ROS format
void cloud_callback (const sensor_msgs::PointCloud2ConstPtr& cloud_msg)
{
  pcl::PointCloud<pcl::PointXYZ> depth;
  pcl::fromROSMsg(*cloud_msg, depth);
  std::cout << "Finding coordinate at X: " << x_coordinate << ", Y: " << y_coordinate << std::endl;
  pcl::PointXYZ p1 = depth.at(x_coordinate, y_coordinate);

  std::cout << "Method for calculating position vector:" << std::endl;
  float position_vector[3] = {p1.x, p1.y, p1.z};
  std::cout << "X " << position_vector[0] << " Y: " << position_vector[1] << " Z: " << position_vector[2] << std::endl;
  float magnitude = sqrt(pow(position_vector[0], 2) + pow(position_vector[1], 2) + pow(position_vector[2], 2));
  std::cout << "Center Distance: " << magnitude << std::endl;
  pub.publish(magnitude);
}

int
main (int argc, char** argv)
{
  // Initialize ROS
  ros::init (argc, argv, "my_pcl_tutorial");
  ros::NodeHandle nh;

  // Create a ROS subscriber for the input point cloud
  ros::Subscriber subPointCloud = nh.subscribe ("/camera/depth_registered/points", 1, cloud_callback);
  ros::Subscriber subXCoordinate = nh.subscribe ("/center_x", 1, x_callback);
  ros::Subscriber subYCoordinate = nh.subscribe ("/center_y", 1, y_callback);
  ros::Subscriber subCenterAngle = nh.subscribe ("/center_image", 1, center_callback);

  // Create a ROS publisher for the output point cloud
  pub = nh.advertise<std_msgs::Float32> ("distance", 1);

  // Spin
  ros::spin ();
}
