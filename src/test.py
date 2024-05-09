#!/usr/bin/env python

import rospy
import qi
import paramiko
from scp import SCPClient
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from tf2_msgs.msg._TFMessage import TFMessage
from sensor_msgs.msg._MultiEchoLaserScan import MultiEchoLaserScan
from sensor_msgs.msg._Imu import Imu
import time
import threading
from geometry_msgs.msg import Twist
import keyboard
import numpy as np
#2024-02-24T060328.807Z.explo


class testPepper:

    def __init__(self, ip_address, port):

        self.session = qi.Session()
        self.session.connect("tcp://{0}:{1}".format(ip_address, port))

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=ip_address, username="nao", password="Han343344^^")
        self.scp = SCPClient(ssh.get_transport())

        self.motion_service = self.session.service("ALMotion")
        self.navigation_service = self.session.service("ALNavigation")
        self.memory_service = self.session.service("ALMemory")
        self.tts_service = self.session.service("ALAnimatedSpeech")
        self.autolife_service = self.session.service("ALAutonomousLife")
        self.posture_service = self.session.service("ALRobotPosture")
        self.motion_service.setOrthogonalSecurityDistance(1)
        self.voice_speed = 100
        self.voice_shape = 100
        self.msg = LaserScan()
        self.msg.header.frame_id = 'base_footprint'
        self.msg.angle_min = -np.pi
        self.msg.angle_max = np.pi
        self.msg.angle_increment = 1./np.pi
        self.msg.ranges = -1*np.ones(360)
        self.autolife_service.setState('disabled') #off
        self.posture_service.goToPosture("Stand", 3.0)
        thread3 = threading.Thread(target=self.head)
        thread3.start()
        self.x = 0
        self.y = 0
        self.w = 0
        
    def say(self, text, bodylanguage="contextual"):
        """Animated say text"""
        configuration = {"bodyLanguageMode":bodylanguage}
        self.tts_service.say(
            "\\RSPD={0}\\ \\VCT={1} \\{2}".format(self.voice_speed, self.voice_shape, text), configuration
        )

    def base(self):
        while True:
            self.say("hi")
            time.sleep(1)

    def talker(self):
        
        rate = rospy.Rate(10) # 10hz
        self.pub_laser = rospy.Publisher('/base_scan', LaserScan, queue_size=100)
        self.pub_odom = rospy.Publisher('/odom', Odometry, queue_size=100)

        # self.pub_imu = rospy.Publisher('/imu', Imu, queue_size=100)
        self.cmd_vel_sub = rospy.Subscriber('/turtle1/cmd_vel', Twist, self.cmd_vel_callback) 
        # rospy.Subscriber('/naoqi_driver/imu/base', Imu, self.callback)
        rospy.Subscriber('/naoqi_driver/laser', LaserScan, self.callback2)
        rospy.Subscriber('/scan', LaserScan, self.callback3)
        # rospy.Subscriber('/naoqi_driver/odom', Odometry, self.callback4)

        
        while not rospy.is_shutdown():
            # hello_str = "hello world %s" % rospy.get_time()
            # rospy.loginfo(hello_str) 
            rate.sleep()

    def callback(self, data):
        # rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data)
        self.data_imu = data
        self.pub_imu.publish(self.data_imu)
        
        pass
    def callback2(self, data):
        self.data_laser =data
        self.pub_laser.publish(self.data_laser)
        # self.pub_laser2.publish(self.data_laser)

    def callback3(self, data):
        self.pub_laser.publish(data)
        # self.pub_laser2.publish(self.data_laser)

    def callback4(self, data):
        self.pub_odom.publish(data)
        # self.pub_laser2.publish(self.data_laser)

    def cmd_vel_callback(self, data):
        rospy.loginfo(data)
        x = data.linear.x
        y = data.linear.y
        w = data.angular.z

        if x != self.x:
            self.motion_service.stopMove()
        elif y != self.y:
            self.motion_service.stopMove()
        elif w != self.w:
            self.motion_service.stopMove()
        else:
            pass

        self.x = x
        self.y = y
        self.w = w
        self.motion_service.move(x*0.02,y*0.02,w*0.1)
        # self.motion_service.move(x,y,w)

        # self.navigation_service.navigateTo(x,y)


    def head(self):
        while True:
            self.motion_service.setStiffnesses("Head",1.0)
            self.motion_service.setAngles("Head",[0.,0.],0.05)
            time.sleep(1)



if __name__ == "__main__":
    rospy.init_node('talker', anonymous=True)


    pepper = testPepper(rospy.get_param('~pepper_ip'), rospy.get_param('~pepper_port'))

    
    # thread = threading.Thread(target=pepper.base)
    # thread.start()

    pepper.talker()

    



