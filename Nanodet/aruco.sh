#!/bin/bash
source ~/zzw/sdx_aruco/cat/devel/setup.bash
roslaunch realsense2_camera rs_rgbd.launch & sleep 6	
### zzw_nodes_run
roslaunch cat camera_detect.launch
exit 0
