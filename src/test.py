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
#2024-02-24T060328.807Z.explo
class testPepper:

    def __init__(self):
        ip_address = "192.168.0.125"
        port = 9559

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
        self.voice_speed = 100
        self.voice_shape = 100


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
        rospy.init_node('talker', anonymous=True)
        rate = rospy.Rate(10) # 10hz
        # self.pub_laser = rospy.Publisher('/scan', LaserScan, queue_size=1000)
        
        self.pub_laser2 = rospy.Publisher('/scan', LaserScan, queue_size=100)
        self.pub_laser = rospy.Publisher('/base_scan', LaserScan, queue_size=100)
        self.pub_imu = rospy.Publisher('/imu', Imu, queue_size=100)

        rospy.Subscriber('/naoqi_driver/imu/base', Imu, self.callback)
        rospy.Subscriber('/naoqi_driver/laser', LaserScan, self.callback2)
        while not rospy.is_shutdown():
            # hello_str = "hello world %s" % rospy.get_time()
            # rospy.loginfo(hello_str) 
            rate.sleep()

    def callback(self, data):
        # rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data)
        self.data_imu = data
        # self.pub_imu.publish(self.data_imu)
        pass
    def callback2(self, data):
        # rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data)
        self.data_laser =data
        self.pub_laser.publish(self.data_laser)
        self.pub_laser2.publish(self.data_laser)


def test():
    while True:
        time.sleep(1)
        print("testing...")


if __name__ == "__main__":
    pepper = testPepper()
    
    thread3 = threading.Thread(target=test)
    thread3.start()
    
    # thread = threading.Thread(target=pepper.base)
    # thread.start()

    pepper.talker()

    



