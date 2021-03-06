#!/usr/bin/env python

import numpy as np
import rospy
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib import pyplot as plt
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import Image
from styx_msgs.msg import TrafficLightArray, TrafficLight
from styx_msgs.msg import Lane
from scipy.spatial import KDTree
from cv_bridge import CvBridge
import cv2

import math

'''
This node is for visualizing data

pip install -U matplotlib

apt-get install x11-apps
apt-get install gnome-calculator
apt-get install qtbase5-dev
apt-get install python-tk
apt-get install python-gtk2-dev
export DISPLAY=:0
'''

LOOKAHEAD_WPS = 200  # Number of waypoints we will publish. You can change this number


class Visual(object):
    def __init__(self):
        rospy.init_node('visual')

        self.pose = None
        self.base_waypoints = None
        self.waypoints_2d = None
        self.waypoint_tree = None
        self.fig = plt.figure(figsize=(15, 15))
        plt.ion()
        plt.show()
        self.table1 = self.fig.add_subplot(2,2,1)
        # x1,x2,y1,y2
        self.table1.axis([0, 2500, 1000, 3100])
        self.table2 = self.fig.add_subplot(2,2,2)
        self.table2.axis([0, 2500, 1000, 3100])
        self.table3 = self.fig.add_subplot(2,2,3)
        self.table4 = self.fig.add_subplot(2,2,4)
        self.waypoints_x = []
        self.waypoints_y = []
        self.pose_x = []
        self.pose_y = []
        self.recent_pose_x = []
        self.recent_pose_y = []
        self.vel_x = []
        self.vel_y = []
        self.lights_x = []
        self.lights_y = []
        self.final_waypoints_x = []
        self.final_waypoints_y = []

        self.has_image = False
        self.cv_image = None
        self.bridge = CvBridge()
        self.lights = None
		
        # prevent refreshing graph while updating pose array
        self.updatelock = 0
        self.start_seconds = rospy.get_time()
        self.last_image_time = rospy.get_time()
        self.image_update = 0
        self.pose_update = 0
        self.vel_update = 0

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)
        rospy.Subscriber('/current_velocity', TwistStamped, self.velocity_cb)
        sub6 = rospy.Subscriber('/image_color', Image, self.image_cb)
        sub3 = rospy.Subscriber('/vehicle/traffic_lights', TrafficLightArray, self.traffic_cb)

        rospy.Subscriber('/final_waypoints', Lane, self.final_waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below

        # TODO: Add other member variables you need below
        self.loop()

    def loop(self):
        rate = rospy.Rate(2)  # can go as low as 30Hz
        while not rospy.is_shutdown():
            if self.pose and self.base_waypoints and self.table1:
                #table1.clear()
                self.table1.plot(self.waypoints_x, self.waypoints_y)
                if self.updatelock == 0:
                    self.table1.plot(self.pose_x, self.pose_y)
                if self.updatelock == 0:
                    self.table1.plot(self.lights_x, self.lights_y)
                if self.updatelock == 0:
                    self.table4.plot(self.vel_x, self.vel_y)
                if (self.updatelock == 0) and self.has_image and (self.image_update == 1):
                    self.table3.cla()
                    self.table3.imshow(self.cv_image)
                    self.image_update = 0

                if self.updatelock == 0:
                    self.table2.cla()
                if self.updatelock == 0:
                    self.table2.plot(self.recent_pose_x, self.recent_pose_y)
                if self.updatelock == 0:
                    self.table2.plot(self.final_waypoints_x, self.final_waypoints_y)

                plt.draw()
                plt.pause(0.001)
            #print("loop")
            rate.sleep()

    def get_closest_waypoint_idx(self):
        x = self.pose.pose.position.x
        y = self.pose.pose.position.y
        closest_idx = self.waypoint_tree.query([x, y], 1)[1]

        # check if closest is ahead or behind vehilcle
        closest_coord = self.waypoints_2d[closest_idx]
        prev_coord = self.waypoints_2d[closest_idx - 1]

        # equation for hyperplane through closest_coords
        cl_vect = np.array(closest_coord)
        prev_vect = np.array(prev_coord)
        pos_vect = np.array([x, y])

        val = np.dot(cl_vect - prev_vect, pos_vect - cl_vect)

        if val > 0:
            closest_idx = (closest_idx + 1) % len(self.waypoints_2d)
        return closest_idx

    def publish_waypoints(self):
        if self.waypoint_tree:
            closest_wp_idx = self.get_closest_waypoint_idx()
            farthest_wp_idx = closest_wp_idx + LOOKAHEAD_WPS

            lane = Lane()
            lane.header = self.base_waypoints.header
            lane.waypoints = self.base_waypoints.waypoints[closest_wp_idx:farthest_wp_idx]
            self.final_waypoints_pub.publish(lane)

    def traffic_cb(self, msg):
        self.lights = msg.lights
        self.updatelock = 1
        self.lights_x = []
        self.lights_y = []		
        for light in self.lights:
            self.lights_x.append(light.pose.pose.position.x);
            self.lights_y.append(light.pose.pose.position.y);
        self.updatelock = 0
			
    def image_cb(self, msg):
        """
        Args:
            msg (Image): image from car-mounted camera

        """
        now_time = rospy.get_time()
        if (self.image_update == 0) and (now_time > (self.last_image_time + 1)):
            self.last_image_time = now_time
            self.has_image = True
            self.updatelock = 1
            self.cv_image = cv2.cvtColor(self.bridge.imgmsg_to_cv2(msg, "bgr8"), cv2.COLOR_BGR2RGB)

            self.cv_image = self.cv_image.astype(int)
            self.cv_image = cv2.normalize(self.cv_image, None, 255,0, cv2.NORM_MINMAX, cv2.CV_8UC1)
            self.updatelock = 0
            self.image_update = 1
		
			
    def pose_cb(self, msg):
        self.pose = msg  # around 50 Hz
        self.updatelock = 1
        self.pose_x.append(msg.pose.position.x)
        self.pose_y.append(msg.pose.position.y)
        if len(self.pose_x) > 21:
            self.recent_pose_x = self.pose_x[-20:]
            self.recent_pose_y = self.pose_y[-20:]
        else:
            self.recent_pose_x = self.pose_x
            self.recent_pose_y = self.pose_y
        self.updatelock = 0
        #print("new pose")

    def velocity_cb(self, msg):
        self.updatelock = 1
        timenow = rospy.get_time() - self.start_seconds
        self.vel_x.append(timenow)
        self.vel_y.append(msg.twist.linear.x)
        self.updatelock = 0
        #print("new vel")
		
    def waypoints_cb(self, waypoints):
        # load base waypoints
        print("new waypoints")
        self.base_waypoints = waypoints
        if not self.waypoints_2d:
            # convert waypoints to (x,y) list
            self.waypoints_2d = [
                [
                    waypoint.pose.pose.position.x,
                    waypoint.pose.pose.position.y
                ] for waypoint in waypoints.waypoints
            ]
            maxdist = 0
            prev_x = -1
            prev_y = -1
            for waypoint in waypoints.waypoints:
                self.waypoints_x.append(waypoint.pose.pose.position.x);
                self.waypoints_y.append(waypoint.pose.pose.position.y);
                if prev_x >= 0:
                    x = waypoint.pose.pose.position.x - prev_x
                    y = waypoint.pose.pose.position.y - prev_y

                    dist = math.sqrt((x*x) + (y*y))
                    if dist > maxdist:
                        maxdist = dist
                prev_x = waypoint.pose.pose.position.x
                prev_y = waypoint.pose.pose.position.y
            # build KDTree
            self.waypoint_tree = KDTree(self.waypoints_2d)
            # for Highway map, maxdist = 2.6486
            print("Waypoints max distance between points = ",maxdist)

    def final_waypoints_cb(self, waypoints):
        self.updatelock = 1
        self.final_waypoints_x = []
        self.final_waypoints_y = []
        for waypoint in waypoints.waypoints:
            self.final_waypoints_x.append(waypoint.pose.pose.position.x);
            self.final_waypoints_y.append(waypoint.pose.pose.position.y);
        self.updatelock = 0

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)
        for i in range(wp1, wp2 + 1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        Visual()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start visual node.')
