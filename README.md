#  introduce

<img src="https://capsule-render.vercel.app/api?type=waving&color=BDBDC8&height=150&section=header" />

*ros-medloic version ros pepper*



#  require

>##  depthimage_to_laserscan(git clone)
https://github.com/ros-perception/depthimage_to_laserscan

>##  ira_laser_tools(git clone)
https://github.com/iralabdisco/ira_laser_tools

>##  ros_navigation(sudo apt install ros-melodic-navigation)
https://github.com/ros-planning/navigation

>##  ros_gmapping(sudo apt install ros-melodic-gmapping)

https://github.com/ros-perception/slam_gmapping

>##  ros_openslam gmapping(sudo apt install ros-melodic-openslam_gmapping)

https://github.com/ros-perception/openslam_gmapping

>##  naoqi_driver(git clone)

https://github.com/ros-naoqi/naoqi_driver

>## pynaoqi(first install!! )
https://www.aldebaran.com/en/support/pepper-naoqi-2-9/downloads-softwares
1. download old:Pepper SDK(for2.5.5 ver)
2. tar -zxvf <filename>
3. export PYTJONPATH=${PYTHONPATH}:~/pynaoqi/lib/python2.7/site-packages  # add at ~/.bashrc file, pynaoqi will be change for version!!!


#  Error solution

Could NOT find SDL (missing: SDL_LIBRARY SDL_INCLUDE_DIR)

>sudo apt-get install libsdl-image1.2-dev
>sudo apt-get install libsdl-dev

Could not find a package configuration file provided by "tf2_sensor_msg

>sudo apt-get install ros-kinetic-tf2-sensor-msgs

CMake error with move_base_msgs

>git clone https://github.com/ros-planning/navigation_msgs.git

naoqi driver catkin_make Error

>sudo apt install ros-melodic-naoqi-driver


