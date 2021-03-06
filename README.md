﻿﻿﻿This is the project repo for the final project of the Udacity Self-Driving Car Nanodegree: Programming a Real Self-Driving Car. For more information about the project, see the project introduction [here](https://classroom.udacity.com/nanodegrees/nd013/parts/6047fe34-d93c-4f50-8336-b70ef10cb4b2/modules/e1a23b06-329a-4684-a717-ad476f0d8dff/lessons/462c933d-9f24-42d3-8bdc-a08a5fc866e4/concepts/5ab4b122-83e6-436d-850f-9f4d26627fd9).
The aim of the project is to enable Carla (Udacity's self driving car) to go around the testtrack using waypoint navigation, stopping at the red lights by controlling throttle brake and steer.

# System Architecture

The following is a system architecture diagram showing the ROS nodes and topics
![alt text](imgs/inference/final-project-ros-graph-v2.png)

The primary nodes are:

### Perception
This takes in feed from the camera and a map of traffic lights. If the car is arriving at a traffic light then the traffic light detector is called to detect the state of the traffic light. The state of the traffic light and the position of the associated stop line are then published.

### Control
Carla is equipped with a drive-by-wire (dbw) system, meaning the throttle, brake, and steering have electronic control. This node is responsible for controlling the car based on the waypoint navigation.

### Waypoint Updater
Purpose of this node is to update the target velocity property of each waypoint based on traffic light and obstacle detection data.

# Team Members
#### Lewis Luyken
`lewisluyken at hotmail dot com`

Team lead and implemented the code to deploy the traffic light detector.

#### Sam Thomas
`samthomasdigital at gmail dot com`

Implemented the partial waypoint updater. Modified the waypoint follower to follow more precisely. Code in branch `st/walkthrough`.

Trained the traffic light detector. Inference speed is ~14ms on a maxQ 1050ti.

Code in repository [https://github.com/swarmt/CarND-Traffic-Light-Detection]
![alt text](imgs/inference/left0000.jpg)
![alt text](imgs/inference/left0027.jpg)



#### Archit Rastogi 
`archit.rstg *at* gmail.com`

Implemented the full waypoint updater. Modified the code to create a final_waypoints message from the base waypoints.
Based on the /traffic_waypoint values, changed the waypoint target velocities to stop the car smoothly before the stop line when it sees a red light. Its done in two steps:

1. Finding the stopline index and assigning zero velocity to that waypoint
2. Smoothly bringing the velocity to zero at that waypoint by decreasing it on the basis of a quadratic function of distance- so that not to exceed the maximum acceleration and jerk levels of 10ms-2 and 10ms-3 respectively



#### Dai Siyang
`sydaioo at hotmail dot com`

Integrated code from team members. Performed trial runs in simulator for both Highway and Test Lot scenarios and provided feedback videos for debugging. Analyzed training rosbag files and simulator ROS messages published.
Assisted Sam in training traffic light detector.

#### Ong Chin Kiat 
`chinkiat *at* gmail.com`

Reduce the chance of car going off road, especially on slow systems, by modifying waypoints to guide the car back on track when the PID controller is failing. Integration testing and debugging.




# Installation

Please use **one** of the two installation options, either native **or** docker installation.

### Native Installation

* Be sure that your workstation is running Ubuntu 16.04 Xenial Xerus or Ubuntu 14.04 Trusty Tahir. [Ubuntu downloads can be found here](https://www.ubuntu.com/download/desktop).
* If using a Virtual Machine to install Ubuntu, use the following configuration as minimum:
  * 2 CPU
  * 2 GB system memory
  * 25 GB of free hard drive space

  The Udacity provided virtual machine has ROS and Dataspeed DBW already installed, so you can skip the next two steps if you are using this.

* Follow these instructions to install ROS
  * [ROS Kinetic](http://wiki.ros.org/kinetic/Installation/Ubuntu) if you have Ubuntu 16.04.
  * [ROS Indigo](http://wiki.ros.org/indigo/Installation/Ubuntu) if you have Ubuntu 14.04.
* [Dataspeed DBW](https://bitbucket.org/DataspeedInc/dbw_mkz_ros)
  * Use this option to install the SDK on a workstation that already has ROS installed: [One Line SDK Install (binary)](https://bitbucket.org/DataspeedInc/dbw_mkz_ros/src/81e63fcc335d7b64139d7482017d6a97b405e250/ROS_SETUP.md?fileviewer=file-view-default)
* Download the [Udacity Simulator](https://github.com/udacity/CarND-Capstone/releases).

### Docker Installation
[Install Docker](https://docs.docker.com/engine/installation/)

Build the docker container
```bash
docker build . -t capstone
```

Run the docker file
```bash
docker run -p 4567:4567 -v $PWD:/capstone -v /tmp/log:/root/.ros/ --rm -it capstone
```

### Port Forwarding
To set up port forwarding, please refer to the [instructions from term 2](https://classroom.udacity.com/nanodegrees/nd013/parts/40f38239-66b6-46ec-ae68-03afd8a601c8/modules/0949fca6-b379-42af-a919-ee50aa304e6a/lessons/f758c44c-5e40-4e01-93b5-1a82aa4e044f/concepts/16cf4a78-4fc7-49e1-8621-3450ca938b77)

### Usage

1. Clone the project repository
```bash
git clone https://github.com/udacity/CarND-Capstone.git
```

2. Install python dependencies
```bash
cd CarND-Capstone
pip install -r requirements.txt
```
3. Make and run styx
```bash
cd ros
catkin_make
source devel/setup.sh
roslaunch launch/styx.launch
```
4. Run the simulator

### Real world testing
1. Download [training bag](https://s3-us-west-1.amazonaws.com/udacity-selfdrivingcar/traffic_light_bag_file.zip) that was recorded on the Udacity self-driving car.
2. Unzip the file
```bash
unzip traffic_light_bag_file.zip
```
3. Play the bag file
```bash
rosbag play -l traffic_light_bag_file/traffic_light_training.bag
```
4. Launch your project in site mode
```bash
cd CarND-Capstone/ros
roslaunch launch/site.launch
```
5. Confirm that traffic light detection works on real life images



