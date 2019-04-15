# senior_design

SSH into Tegra:
  ```
  ssh -Y nvidia@tegra-ubuntu
  ```
  
Steps to push to GitHub:
  1. Go to the root of the folder:
  ```
  cd ~/catlin_ws/src/senior_design
  ```
  2. Update your repository
  ```
  git pull
  ```
  3. Add your changes
  ```
  git add .
  ```
  4. Commit your changes with an appropriate commit message
  ```
  git commit -m "YOUR MESSAGE HERE"
  ```
  5. Push your changes
  ```
  git push
  ```
  
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
  6. Launch Rplidar
  ```
  roslaunch rplidar_ros rplidar.launch
  ``` 
  7. Launch Laser scan splitter
  ```
  roslaunch laser_values laser.launch
  ```
  8. Run Rplidar Scan 
  ```
  python scan.py
  ```
  9. Run Kobuki
  ```
  python controller.py
  ````
Running Alexa Skill w/ ngrok:
  1. run python script
  ```
  python lambda_function.py
  ```
  2. launch ngrok tunnel
  ```
  ./ngrok http 5000
  ```
  3. add https://.......ngrok.io to endpoints
