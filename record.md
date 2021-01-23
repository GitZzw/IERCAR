d435：(sudo apt install ros-melodic-rgbd-launch)roslaunch realsense2_camera rs_camera.launch


nanodet：
	虚拟环境：conda activate zzw4(python=3.6，3.6才能用pyrealsense库)
	(source /opt/intel/openvino_2020.4.287/bin/setupvars.sh)

	openino不完整库影响正常opencv，在cmakelist添加  set(OpenCV_DIR "/usr/share/OpenCV")

	

	python3 de.py webcam --model model/model_last.pth --config config/test.yml  --path 0(usb相机输入)

	python3 d435msgth2.py webcam --model model/drone.pth --config config/test.yml  --path 0(pyrealsense库d435输入)

	python client2.py


acuco：(zzw5)
	编译(catkin_make -DPYTHON_EXECUTABLE=/usr/bin/python2)
	source 一下包
	roslaunch cat camera_detect.launch 



https://blog.csdn.net/HHH_LLL/article/details/106619456


uwb:
source ~/zzw/catkin_workspace/devel/setup.bash

roslaunch nlink_parser linktrack.launch

rosrun nlink_example linktrack_example


compare:
source aruco msg
conda activate zzw5
python compare.py



 rosbag record /camera/color/image_raw /aruco_detectend_data_small /trans /yolo_target_corner

