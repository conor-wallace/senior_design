# senior_design

Steps to run kobuki steering method all in different terminals:
  1. Launch Roscore
  ```
  roscore
  ```
  2. Launch Intel Camera
  ```
  roslaunch realsense2_camera rs_rgbd.launch
  ```
  3. Launch Yolo
  ```
  roslaunch darknet_ros yolo_v3.launch
  ```
  4. Run Steering Algorithm
  ```
  python cam_node.py
  ```
  5. Connect to Kobuki 
  ```
  roslaunch kobuki_node minimal.launch
  ```
  6. Run rplidar sacn 
  ```
  python scan.py
  ```
  7. Launch Laser scan splitter
  ```
  roslaunch laser_values laser.launch
  ```
  8. Run Kobuki
  ```
  python controller.py
  ````
