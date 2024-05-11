#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import Tkinter
import threading
import sys
import cv2
from flask import Flask, render_template, redirect, url_for, request
import socket
import speech_recognition as sr
import os

#2024-02-24T060328.807Z.explo
tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp_files")
print("tmp_path:", tmp_path)
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)
    print("Created temporary folder Pepper_Controller/pepper/tmp_files/ for retrieved data")


############################################################################################

#flask web server


app = Flask(__name__)
web_host = "192.168.122.56"
web_page = "http://192.168.122.56:8080/"


@app.route('/', methods=['GET', 'POST'])
def main_page():
    return render_template('start.html')

@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        app.start = True
        return render_template('main.html')
    return redirect(url_for('main_page'))

@app.route('/test1', methods=['GET', 'POST'])
def test1():
    if request.method == 'POST':
        app.test2 = 1  
        return render_template('main.html')
    return redirect(url_for('main_page'))
    
@app.route('/test2', methods=['GET', 'POST'])
def test2():
    if request.method == 'POST':
        app.test2 = 2
        return render_template('main.html')
    return redirect(url_for('main_page'))



#플라스크 변수: 전역변수랑 같음(웹 이벤트 작동 시 사용)
app.test2 = 0
app.start = False
############################################################################################



class RosKuPepper:

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


        
        self.user_session = self.session.service("ALUserSession")
        self.sonar_service = self.session.service("ALLocalization")
        self.sound_detect_service = self.session.service("ALSoundDetection")
        self.detect_service = self.session.service("ALVisualCompass")
        self.posture_service = self.session.service("ALRobotPosture")
        self.tracker_service = self.session.service("ALTracker")
        self.tts_service = self.session.service("ALAnimatedSpeech")
        self.tablet_service = self.session.service("ALTabletService")
        self.system_service = self.session.service("ALSystem")
        self.battery_service = self.session.service("ALBattery")
        self.awareness_service = self.session.service("ALBasicAwareness")
        self.led_service = self.session.service("ALLeds")
        self.audio_device = self.session.service("ALAudioDevice")
        self.camera_device = self.session.service("ALVideoDevice")
        self.face_detection_service = self.session.service("ALFaceDetection")
        self.audio_service = self.session.service("ALAudioPlayer")
        self.animation_service = self.session.service("ALAnimationPlayer")
        self.behavior_service = self.session.service("ALBehaviorManager")
        self.face_characteristic = self.session.service("ALFaceCharacteristics")
        self.people_perception = self.session.service("ALPeoplePerception")
        self.speech_service = self.session.service("ALSpeechRecognition")
        self.dialog_service = self.session.service("ALDialog")
        self.audio_recorder = self.session.service("ALAudioRecorder")
        self.text_to_speech = self.session.service("ALTextToSpeech")
        self.autonomous_life_service = self.session.service("ALAutonomousLife")

        self.slam_map = None
        self.localization = None
        self.camera_link = None

        self.recognizer = sr.Recognizer()
        self.autonomous_blinking_service = self.session.service("ALAutonomousBlinking")
        self.eye_blinking_enabled = True

        self.voice_speed = 100
        self.voice_shape = 100



        self.motion_service.setOrthogonalSecurityDistance(1)
        self.voice_speed = 100
        self.voice_shape = 100
        self.msg = LaserScan()
        self.msg.header.frame_id = 'base_footprint'
        self.msg.angle_min = -np.pi
        self.msg.angle_max = np.pi
        self.msg.angle_increment = 1./np.pi
        self.msg.ranges = -1*np.ones(360)
        # self.autolife_service.setState('disabled') #off
        self.posture_service.goToPosture("Stand", 3.0)
        thread3 = threading.Thread(target=self.head)
        thread3.start()
        self.x = 0
        self.y = 0
        self.w = 0

        self.event = threading.Event()
        socket_thread = threading.Thread(target=self.socket_Server_connect)
        socket_thread.start()
        self.base_thread = threading.Thread(target=self.baseline)
        self.base_thread.daemon = True
        self.base_thread.start()
        self.say("hi my name is pepper.")

        #GUI
        self.window = Tkinter.Tk()
        self.base_interface_robot()
        self.result_map= 0 
        self.resolution=0 
        self.offset_x =0 
        self.offset_y =0


    def stopThreadUntilOneTheEnd(self):
        if self.event.is_set():
            while True:
                if self.event.is_set():
                    time.sleep(0.1)
                else:
                    break

    #현재 상태 출력 모음
    def status_print(self):
        print("focus activity:", self.robot.autonomous_life_service.focusedActivity())
        print("context:", self.robot.memory_service.getData('Diagnosis/Temperature/Tablet/Error'))
        # print("key list:", self.robot.memory_service.getDataListName( ))
        # print("context:", self.robot.autonomous_life_service.getFocusHistory())    
        # print("context:", self.robot.autonomous_life_service.getFocusContext())
        # print("laser x:", self.robot.memory_service.getData("Device/SubDeviceList/Platform/LaserSensor/Front/Vertical/Right/Seg01/X/Sensor/Value"))
        # print("laser y:", self.robot.memory_service.getData("Device/SubDeviceList/Platform/LaserSensor/Front/Vertical/Right/Seg01/Y/Sensor/Value"))
        print("laser front value:", self.robot.memory_service.getData("Device/SubDeviceList/Platform/LaserSensor/Front/Reg/Status/Sensor/Value"))
        print("usersession:", self.robot.user_session.getOpenUserSessions())
        print("front sonar value:", self.robot.memory_service.getData("Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value"))

    #기본 파라미터 구성
    def base_parameter(self):
        
        self.set_security_distance(distance=0.2)
        self.set_vocabulary()

        try:
            self.dialog_service.unsubscribe("my_dialog") #start dialog engine
        except:
            pass

        self.text_to_speech.setLanguage("Korean") #타블렛 화면도 한글로 
        topicContent2 = ("topic: ~mytopic2()\n"
                            "language: enu\n"
                            "proposal: This is KUPepper, How to help you??\n")
        self.autonomous_life_service.setState("interactive")
        self.autonomous_life_service.switchFocus("web_site-9108dc/behavior_1") #package-uuid/behavior-path
        loaded_topic=self.dialog_service.loadTopicContent(topicContent2) #load topic content
        self.dialog_service.activateTopic(loaded_topic) #activate topic
        

        self.dialog_service.subscribe("my_dialog") #start dialog engine
        # self.load_map_and_localization()

        # print(self.robot.navigation_service.getMetricalMap())

    #페퍼 상호작용
    def interaction(self):
        #머리 터치 시 상호작용
        if self.memory_service.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value"):
            self.say("무슨 일이신가요?")
    
    #웹 상호작용
    def web_interaction(self):
        #이동 상호작용
        # print("interaction number: ", app.test2)
        if app.test2 == 1:
            app.test2 = 0
            self.navigation_mode_button_web()
        elif app.test2 == 2:
            app.test2 = 0
            self.talk_pepper_web()
     
    #기본 루프
    def baseline(self):
        while_count = 0
        print("!")
        self.base_parameter()
        try:
            while True:
                if app.start == True:
                    if while_count == 0:
                        self.say("반갑습니다. 페퍼를 동작합니다")
                        self.start_animation(np.random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"]))
                    self.stopThreadUntilOneTheEnd()
                    # self.status_print()
                    # self.base_move()
                    self.web_interaction()
                    self.interaction()
                    word =self.memory_service.getData("WordRecognized")
                    # print(word) #확인용
                    # if self.robot.memory_service.getData("ALSpeechRecognition/Status") == "SpeechDetected":
                    #     self.talk_pepper()
                    if word[1]>=0.40:
                        self.say("네에, 말씀하세요.")
                        talk_thread = threading.Thread(target=self.talk_pepper)
                        talk_thread.daemon = True
                        talk_thread.start()
                    time.sleep(0.1)
                    while_count += 1
                else:
                    print("wait...")
                    time.sleep(1)

        except KeyboardInterrupt:
            #stop
            self.say("연결을 중지합니다")
            sys.exit(0)
        print("exit")


    #맵 종류
    #2024-02-14T082317.984Z.explo(8층 pbl실 기본 explore() 맵)
    #2024-02-16T133625.109Z.explo(앞 부분만 찍은 explore() 맵)
        #2024-02-16T140640.347Z.explo
        #2024-02-16T140903.087Z.explo( 의자로 맵 만든 거 explore())
        #2014-04-04T023359.452Z.explo( 의자로 맵 만든 거2)
        #2014-04-04T030206.953Z.explo(세번째)
        #2024-02-27T084209.829Z.explo 방향 확인 하기 위한 임시 =

    #맵 로드 후 로컬라이제이션
    def load_map_and_localization(self):
        self.event.set()
        self.stop_localization()
        self.load_map(file_name="2024-02-14T082317.984Z.explo")
        self.first_localization()
        self.event.clear()

    def session_reset(self):
        self.session.reset

    #gpt
    def talk_pepper_web(self):
        self.event.set()
        try: 
            self.recordSound()
            self.download_file("speech.wav")
            r = sr.Recognizer()
            kr_audio = sr.AudioFile("./tmp_files/speech.wav")
            with kr_audio as source:
                audio = r.record(source)
            # self.robot.say(r.recognize_google(audio, language='ko-KR').encode('utf8'))
            msg2 = r.recognize_google(audio, language='ko-KR')
            self.client_soc.sendall(msg2.encode(encoding='utf-8'))
            data = self.client_soc.recv(1000)#메시지 받는 부분
            self.say(data)
        except:
            print("Maybe Pepper didn't hear anything")

        self.event.clear()

   


    def talk_pepper(self):
        self.event.set()

        try:
            self.audio_recorder.stopMicrophonesRecording()
        except:
            pass
    
        self.audio_recorder.startMicrophonesRecording("/home/nao/speech.wav", "wav", 48000, (0, 0, 1, 0))
        time.sleep(1)
        #여기서 endofprocess가 나올때까지 기다리는데 일정시간 지나면 끝내는 코드를 넣어야함
        listenOffCount = 0
        while True:
            print(self.memory_service.getData("ALSpeechRecognition/Status"))
            if self.memory_service.getData("ALSpeechRecognition/Status") == "EndOfProcess":
                self.audio_recorder.stopMicrophonesRecording()
                break
            if self.memory_service.getData("ALSpeechRecognition/Status") == "ListenOff":
                listenOffCount += 1
            if listenOffCount == 3:
                    self.audio_recorder.stopMicrophonesRecording()
                    break  

        # self.robot.audio_service.playFile("/home/nao/speech.wav") #mp3파일 재생 확인용
        self.download_file("speech.wav")
        r = sr.Recognizer()
        kr_audio = sr.AudioFile("{}/speech.wav".format(tmp_path))
        with kr_audio as source:
            audio = r.record(source)
        # self.robot.say(r.recognize_google(audio, language='ko-KR').encode('utf8'))
        #여기서 recognize로 인식하는데 인식못했을때는 죄송합니다 하고 다시 인식하게 만들어야함
        try:
            msg2 = r.recognize_google(audio, language='ko-KR') #음성을 변환
            print("send message!!!!~~~")
            self.client_soc.sendall(msg2.encode(encoding='utf-8'))
            data = self.client_soc.recv(1000)#메시지 받는 부분
            self.say(data)
            print(data)
            # self.talk_pepper()#또다시 인식
        except:
            self.say("죄송합니다. 다시 말해주시겠습니까?") #인식못했을때
            # self.talk_pepper()# 다시 인식
        finally:
            self.event.clear()
            time.sleep(0.1)



    def set_vocabulary(self):
    #setVocabulary
        self.speech_service.pause(True) 
        self.speech_service.removeAllContext() #context를 지워야하는지 몰루
        self.speech_service.deleteAllContexts()
        self.speech_service.setVocabulary(["cooper",'pepper'],False) #true 하면 "<...> hi <...>" 이렇게 나옴
        self.speech_service.pause(False)

    #error
    def sonar_getdata(self):
        print("sonarleft" , self.robot.sonar_service.SonarLeftDetected())
        print("sonarright" ,self.robot.sonar_service.SonarRightDetected())
        print("sonarnothingleft", self.robot.sonar_service.SonarLeftNothingDetected())
        print("sonarnothingright",self.robot.sonar_service.SonarRightNothingDetected())
        pass

    #no need
    def security_data(self):
        print("othogna:" ,self.robot.motion_service.getOrthogonalSecurityDistance())
        print("tangential:" ,self.robot.motion_service.getTangentialSecurityDistance())
        print("enable security: ", self.robot.motion_service.getExternalCollisionProtectionEnabled("All"))
        # print("aa: ", self.robot.motion_service.isCollision())


    #기본 움직임
    def base_move(self):
        # print((round(self.robot.motion_service.getAngles("HeadPitch", True)[0],1)+0.5)*10)
        # self.robot.motion_service.move(0,0,(round(self.robot.motion_service.getAngles("HeadPitch", True)[0],1)+0.5)*10)
        # self.robot.motion_service.move(1,0,0)
        print((round(self.robot.motion_service.getAngles("HeadYaw", True)[0],1)))
        self.motion_service.move(0,0,(round(self.robot.motion_service.getAngles("HeadYaw", True)[0],1)))
        self.motion_service.move(1,0,0)


    #GUI에 기능 적용
    def base_interface_robot(self):
        self.window.geometry("400x200")
        self.window.title("pepper")
        self.frame_1 = Tkinter.Frame(self.window)
        self.frame_1.pack(side="top")
        self.frame_2 = Tkinter.Frame(self.window)
        self.frame_2.pack(side="top")
        self.exploration_pepper_button()
        self.navigation_pepper_button()
        self.webpage_reset_button()
        self.show_map_button()
        self.slam_start_button()
        self.slam_stop_button()


        #마지막에 있어야함
        self.window.mainloop()

    def exploration_mode_button_push(self, text):
        try:
            self.event.set()
            result = text.get("1.0", "end")
            self.exploration_mode(int(result))
        except: 
            pass
        self.event.clear()

    def navigation_mode_button_web(self):
        self.event.set()
        move_pepper = threading.Thread(target=self.move(0, 0))
        self.event.clear()
        
    def navigation_mode_button_push(self,text,text2):
        
        self.event.set()
        x = text.get("1.0", "end")
        y = text.get("1.0", "end")
        move_pepper = threading.Thread(target=self.move(int(x),int(y)))
        move_pepper.start()

        self.event.clear()


    def show_map_button_push(self):
        self.event.set()               
        show_map_thread = threading.Thread(target=self.show_map)
        show_map_thread.start()
        show_map_thread.join()
        imshow_map_thread = threading.Thread(target=self.imshow_map)
        imshow_map_thread.start()   
        self.event.clear()

    def imshow_map(self):
            cv2.imshow("RobotMap", self.robot_map)
            cv2.setMouseCallback("RobotMap", self.mouse_callback)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flags, param):
        # 마우스 왼쪽 버튼을 클릭할 때
        if event == cv2.EVENT_LBUTTONDOWN:
            # map_y = (x * self.robot.resolution + self.robot.offset_x)
            # map_x = (y * self.robot.resolution - self.robot.offset_y)
            map_x = (x * self.resolution + self.offset_x)
            map_y = -1 * (y * self.resolution - self.offset_y)
            # map_x = x
            # map_y = y
            print("mouse click:", map_x, map_y)
            self.move(map_x,map_y)
            pos = self.pos[0]
            goal_x = (pos[0] - self.offset_x) / self.resolution
            goal_y = -1 * ((pos[1] - self.offset_y) / self.resolution)
            self.robot_map = cv2.circle(self.robot_map, (int(goal_x), int(goal_y)), 3, (255, 0, 0), -1)
            self.show_map_button_push()

    def web_page_reset(self):
        self.event.set()
        self.web_thread = threading.Thread(target=self.show_web(web_page))
        self.web_thread.start()     
        self.say("web page reset")
        self.event.clear()

    def move(self,x,y):
        try:
            self.event.set()
            self.navigate_to(x, y)
            map_x = (x * self.resolution)
            map_y = -1 * (y * self.resolution)
            # map_x = x
            # map_y = y
            print("mouse click:", map_x, map_y)
            pos = self.pos[0]
            goal_x = (pos[0] - self.offset_x) / self.resolution
            goal_y = -1 * ((pos[1] - self.offset_y) / self.resolution)
            self.robot_map = cv2.circle(self.robot_map, (int(goal_x), int(goal_y)), 3, (255, 0, 0), -1)
            self.show_map_button_push()
        except:
            print("open the map first")
        self.event.clear()

    def slam_start_button_push(self):
        self.event.set()
        self.slam_start_thread = threading.Thread(target=self.slam(status=True))
        self.event.clear()

    def slam_stop_button_push(self):
        self.event.set()
        self.slam_stop_thread = threading.Thread(target=self.slam(status=False))
        self.event.clear()

    def session_reset(self):
        self.session.reset
 

    #gui 기능(버튼 등) 설계
    def navigation_pepper_button(self):
        text = Tkinter.Text(self.frame_2, height =1, width= 5)
        text2 = Tkinter.Text(self.frame_2, height =1, width= 3)
        button = Tkinter.Button(self.frame_2, text="이동(x,y)", command=lambda: self.navigation_mode_button_push(text, text2))
        button.grid(row=1, column=1)
        text.grid(row=1, column=2)
        text2.grid(row=1, column=3)
        self.window.bind("<")
        
    def exploration_pepper_button(self):
        text = Tkinter.Text(self.frame_1, height =1, width= 5)
        button = Tkinter.Button(self.frame_1, text="맵핑 모드", command=lambda: self.exploration_mode_button_push(text))
        button.grid(row=1,column=1)
        text.grid(row=1,column=2)
        self.window.bind("<")

    def webpage_reset_button(self):
        button = Tkinter.Button(self.window, text="웹페이지 리셋", command=self.web_page_reset)
        button.pack()
        self.window.bind("<")

    def show_map_button(self):
        button = Tkinter.Button(self.window, text="맵 확인", command=self.show_map_button_push)
        button.pack()
        self.window.bind("<")

    def slam_start_button(self):
        button = Tkinter.Button(self.window, text="수동 맵핑 시작", command=self.slam_start_button_push)
        button.pack()
        self.window.bind("<")

    def slam_stop_button(self):
        button = Tkinter.Button(self.window, text="수동 맵핑 중지", command=self.slam_stop_button_push)
        button.pack()
        self.window.bind("<")
        # label = Tkinter.Label(self.window, text="안녕하세요!")
        # # 레이블 위치 설정
        # label.place(x=150, y=150)
        # 버튼 위치 설정
        # button.place(x=180, y=200)

    def socket_Server_connect(self):
            host = web_host
            port = 3333

    # 서버소켓 오픈/ netstat -a로 포트 확인
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))

    # 클라이언트 접속 준비 완료
            server_socket.listen(1)

            print('echo server start')

    #  클라이언트 접속 기다리며 대기 
            self.client_soc, addr = server_socket.accept()
            print('connected client addr:', addr)

            while True:
                time.sleep(999999)
            print('서버 종료.')
            # socket_Server_connect.close()

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
        # self.motion_service.move(x*0.02,y*0.02,w*0.1)
        self.motion_service.move(x*0.2,y*0.2,w*2)

        # self.navigation_service.navigateTo(x,y)


    def head(self):
        while True:
            self.motion_service.setStiffnesses("Head",1.0)
            self.motion_service.setAngles("Head",[0.,0.],0.05)
            time.sleep(1)


    def show_image(self, image):
        self.tablet_service.showImage(image)

    def play_video(self, url):
        self.tablet_service.playVideo(url)

    def stop_video(self):
        self.tablet_service.stopVideo()

    def set_korean_language(self):
        self.dialog_service.setLanguage("Korean")
        print("korean language was set up")

    def set_english_language(self):
        self.dialog_service.setLanguage("English")
        print("English language was set up")


    def say(self, text, bodylanguage="contextual"):
        """Animated say text"""
        configuration = {"bodyLanguageMode":bodylanguage}
        self.tts_service.say(
            "\\RSPD={0}\\ \\VCT={1} \\{2}".format(self.voice_speed, self.voice_shape, text), configuration
        )

    def getVoiceSpeed(self):
        return self.voice_speed

    def getVoiceShape(self):
        return self.voice_shape

    def getVoiceVolume(self):
        return self.audio_device.getOutputVolume()

    def test_say(self, sentence, speed=100, shape=100):
        self.tts_service.say(
            ("\\RSPD={0}\\ \\VCT={1} \\" + sentence).format(speed, shape)
        )

    def stand(self):
        """Get robot into default standing position known as `StandInit` or `Stand`"""
        self.posture_service.goToPosture("Stand", 1.0)
        print("[INFO]: Robot is in default position")

    def rest(self):
        """Get robot into default resting position know as `Crouch`"""
        self.posture_service.goToPosture("Crouch", 1.0)
        print("[INFO]: Robot is in resting position")

    def point_at(self, x, y, z, effector_name, frame):
        """
        Point end-effector in cartesian space
        :Example:
        >>> pepper.point_at(1.0, 1.0, 0.0, "RArm", 0)
        """
        speed = 0.5  # 50 % of speed
        self.tracker_service.pointAt(effector_name, [x, y, z], frame, speed)

    def turn_around(self, speed):
        """
        Turn around its axis
        :param speed: Positive values to right, negative to left # other way
        :type speed: float
        """
        self.motion_service.move(0, 0, speed)

    def autonomous_blinking(self):
        self.eye_blinking_enabled = not self.eye_blinking_enabled
        if self.speech_service.getAudioExpression():
            print("Disable eye blinking and beeping when listening...")
            self.speech_service.setAudioExpression(False)
            self.speech_service.setVisualExpression(False)
        else:
            print("Enable eye blinking and beeping when listening...")
            self.speech_service.setAudioExpression(True)
            self.speech_service.setVisualExpression(True)

    def greet(self):
        """
        Robot will randomly pick and greet user
        :return: True or False if action was successful
        """
        print("Robot is into greet")
        animation = np.random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"])
        try:
            animation_finished = self.animation_service.run("animations/[posture]/Gestures/" + animation, _async=True)
            animation_finished.value()
            return True
        except Exception as error:
            print(error)
            return False
    def show_web(self, website):
        print("Showing a website on the tablet")
        self.tablet_service.showWebview(website)
    def detect_touch(self):
        react_to_touch = ReactToTouch(self.app)
        print("Waiting for touch...")
        while not react_to_touch.activated_sensor:
            if react_to_touch.touch != None:
                pass
            else:
                print("Touch callback does not yet work with Python3, please run the code with Python2.7")
                return None
        return react_to_touch.activated_sensor

    def tablet_show_settings(self):
        """Show robot settings on the tablet"""
        self.tablet_service.showWebview("http://198.18.0.1/")

    def reset_tablet(self):
        print("Resetting a tablet view")
        self.tablet_service.hideWebview()
        self.tablet_service.hideImage()

    def stop_behaviour(self):
        """Stop all behaviours currently running"""
        print("Stopping all behaviors")
        self.behavior_service.stopAllBehaviors()

    def dance(self):
        """Start dancing with robot"""
        print("Robot is about to dance a little")
        self.behavior_service.startBehavior("date_dance-896e88/.")
    
    def mood_happy(self):
        """ is happy """
        print("Robot is in happy mood")
        animation_finished = self.animation_service.run("animations/Stand/Emotions/Positive/Happy_4", _async=True)
        animation_finished.value()
        
    
    def autonomous_life(self):
        """
        Switch autonomous life on/off
        """
        state = self.autonomous_life_service.getState()
        if state == "disabled":
            print("Enabling the autonomous life")
            self.autonomous_life_service.setState("interactive")
        else:
            print("Disabling the autonomous life")
            self.autonomous_life_service.setState("disabled")
            self.stand()

    def restart_robot(self):
        """Restart robot (it takes several minutes)"""
        print("[WARN]: Restarting the robot")
        self.system_service.reboot()

    def shutdown_robot(self):
        """Turn off the robot completely"""
        print("[WARN]: Turning off the robot")
        self.system_service.shutdown()

    def autonomous_life_off(self):
        """
        Switch autonomous life off

        .. note:: After switching off, robot stays in resting posture. After \
        turning autonomous life default posture is invoked
        """
        self.autonomous_life_service.setState("disabled")
        self.stand()
        print("[INFO]: Autonomous life is off")

    def autonomous_life_on(self):
        """Switch autonomous life on"""
        self.autonomous_life_service.setState("interactive")
        print("[INFO]: Autonomous life is on")

    def set_volume(self, volume):
        """
        Set robot volume in percentage

        :param volume: From 0 to 100 %
        :type volume: integer
        """
        self.audio_device.setOutputVolume(volume)
        #self.say("Volume is set to " + str(volume) + " percent")
        #self.say("Volume is set to " + str(volume) + " percent")

    def battery_status(self):
        """Say a battery status"""
        battery = self.battery_service.getBatteryCharge()
        language = self.dialog_service.getLanguage()
        if language == "Czech":
            self.say("Mám nabitých " + str(battery) + " procent baterie")
        elif language == "English":
            self.say("My battery level is " + str(battery) + " %")
        
    def blink_eyes(self, rgb):
        """
        Blink eyes with defined color

        :param rgb: Color in RGB space
        :type rgb: integer

        :Example:

        >>> pepper.blink_eyes([255, 0, 0])

        """
        self.led_service.fadeRGB('AllLeds', rgb[0], rgb[1], rgb[2], 1.0)

    def turn_off_leds(self):
        """Turn off the LEDs in robot's eyes"""
        self.blink_eyes([0, 0, 0])
    
    
    
    def start_animation(self, animation):
        """
        Starts a animation which is stored on robot

        .. seealso:: Take a look a the animation names in the robot \
        http://doc.aldebaran.com/2-5/naoqi/motion/alanimationplayer.html#alanimationplayer

        :param animation: Animation name
        :type animation: string
        :return: True when animation has finished
        :rtype: bool
        """
        try:

            if self.eye_blinking_enabled:
                self.speech_service.setAudioExpression(True)
                self.speech_service.setVisualExpression(True)
            else:
                self.speech_service.setAudioExpression(False)
                self.speech_service.setVisualExpression(False)

            animation_finished = self.animation_service.run("animations/[posture]/Gestures/" + animation, _async=True)
            animation_finished.value()

            return True
        except Exception as error:
            print(error)
            return False
    
    def start_behavior(self, behavior):
        """
        Starts a behavior stored on robot

        :param behavior: Behavior name (id/behavior_1 (first part in Choregraphe)
        :type behavior: string
        """
        self.behavior_service.startBehavior(behavior)

    def list_behavior(self):
        """Prints all installed behaviors on the robot"""
        print(self.behavior_service.getBehaviorNames())

    def get_robot_name(self):
        """
        Gets a current name of the robot

        :return: Name of the robot
        :rtype: string
        """
        name = self.system_service.robotName()
        if name:
            self.say("My name is " + name)
        return name

    def hand(self, hand, close):
        """
        Close or open hand

        :param hand: Which hand
            - left
            - right
        :type hand: string
        :param close: True if close, false if open
        :type close: boolean
        """
        hand_id = None
        if hand == "left":
            hand_id = "LHand"
        elif hand == "right":
            hand_id = "RHand"

        if hand_id:
            if close:
                self.motion_service.setAngles(hand_id, 0.0, 0.2)
                print("[INFO]: Hand " + hand + "is closed")
            else:
                self.motion_service.setAngles(hand_id, 1.0, 0.2)
                print("[INFO]: Hand " + hand + "is opened")
        else:
            print("[INFO]: Cannot move a hand")

    def track_object(self, object_name, effector_name, diameter=0.01):
        """
        Track a object with a given object type and diameter. If `Face` is
        chosen it has a default parameters to 15 cm diameter per face. After
        staring tracking in will wait until user press ctrl+c.

        .. seealso:: For more info about tracking modes, object names and other:\
        http://doc.aldebaran.com/2-5/naoqi/trackers/index.html#tracking-modes

        :Example:

        >>> pepper.track_object("Face", "Arms")

        Or

        >>> pepper.track_object("RedBall", "LArm", diameter=0.1)

        :param object_name: `RedBall`, `Face`, `LandMark`, `LandMarks`, `People` or `Sound`
        :param effector_name: `LArm`, `RArm`, `Arms`
        :param diameter: Diameter of the object (default 0.05, for face default 0.15)
        """
        if object == "Face":
            self.tracker_service.registerTarget(object_name, 0.15)
        else:
            self.tracker_service.registerTarget(object_name, diameter)

        self.tracker_service.setMode("Move")
        self.tracker_service.track(object_name)
        self.tracker_service.setEffector(effector_name)

        self.say("Show me a " + object_name)
        print("[INFO]: Use Ctrl+c to stop tracking")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[INFO]: Interrupted by user")
            self.say("Stopping to track a " + object_name)

        self.tracker_service.stopTracker()
        self.unsubscribe_effector()
        self.say("Let's do something else!")

    def take_picture(self):
        self.subscribe_camera("camera_top", 2, 30)
        img = self.get_camera_frame(show=False)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.unsubscribe_camera()
        print(os.getcwd())
        self.play_sound("D://Pepper_Controller_main/camera1.mp3")
        im = Image.fromarray(img)
        photoName = str(random.randint(0, 1000)) + ".png"
        print("Image saved as {}".format(photoName))
        im.save(photoName)
        return photoName

    #수동 slam 모드
    def slam(self, status):

        if status == True:
            self.navigation_service.startMapping()
        else:
            self.navigation_service.stopExploration()
            map_file = self.navigation_service.saveExploration()
            print("[INFO]: Map file stored: " + map_file)


    def exploration_mode(self, radius):
        """
        Start exploration mode when robot it performing a SLAM
        in specified radius. Then it saves a map into robot into
        its default folder.

        .. seealso:: When robot would not move maybe it only needs \
        to set smaller safety margins. Take a look and `set_security_distance()`

        .. note:: Default folder for saving maps on the robot is: \
        `/home/nao/.local/share/Explorer/`

        :param radius: Distance in meters
        :type radius: integer
        :return: image
        
        :rtype: cv2 image
        """
        self.say("Starting exploration in " + str(radius) + " meters")
        self.user_session.getFocusedUser()
        self.navigation_service.explore(radius)
        map_file = self.navigation_service.saveExploration()
        
        print("[INFO]: Map file stored: " + map_file)

        self.navigation_service.startLocalization()

        self.navigation_service.navigateToInMap([0., 0., 0.])
        self.navigation_service.stopLocalization()

        # Retrieve and display the map built by the robot
        result_map = self.navigation_service.getMetricalMap()
        map_width = result_map[1]
        map_height = result_map[2]
        img = numpy.array(result_map[4]).reshape(map_width, map_height)
        img = (100 - img) * 2.55  # from 0..100 to 255..0
        img = numpy.array(img, numpy.uint8)

        self.slam_map = img

    def show_map(self, on_robot=False, remote_ip="lcoalhost"):
        """
        Shows a map from robot based on previously loaded one
        or explicit exploration of the scene. It can be viewed on
        the robot or in the computer by OpenCV.

        :param on_robot: If set shows a map on the robot
        :type on_robot: bool
        :param remote_ip: IP address of remote (default None)
        :type remote_ip: string

        .. warning:: Showing map on the robot is not fully supported at the moment.
        """
        result_map = self.navigation_service.getMetricalMap()
        map_width = result_map[1]
        map_height = result_map[2]
        img = numpy.array(result_map[4]).reshape(map_width, map_height)
        img = (100 - img) * 2.55  # from 0..100 to 255..0
        img = numpy.array(img, numpy.uint8)

        resolution = result_map[0]
        #
        self.robot_localization()

        offset_x = result_map[3][0]
        offset_y = result_map[3][1]

        #현재 localize된 pepper 좌표
        x = self.localization[0]
        y = self.localization[1]
        # print("resolution:", resolution)
        # print("offset_x:", offset_x)
        # print("offset_y:", offset_y)
        # print("x:",x)
        # print("y:",y)

        #지도 상 좌표
        goal_x = (x - offset_x) / resolution
        goal_y = -1 * (y - offset_y) / resolution
        print("goal_x:",goal_x)
        print("goal_y:",goal_y)

        # print(goal_x * resolution + offset_x)
        # print(-1 * (goal_y * resolution - offset_y))

        center_x = (self.localization_first[0] - offset_x) / resolution
        center_y = -1 *(self.localization_first[1] - offset_y) / resolution
        import math
        angle = self.localization2[2]
        angle = math.degrees(angle)
        center = (goal_x , goal_y)
        M = cv2.getRotationMatrix2D(center, 45, 1)
        rotated = cv2.warpAffine(img, M, (map_width, map_height))
        img = rotated


        
        
        
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        cv2.circle(img, (int(center_x), int(center_y)), 3, (0, 0, 255), -1)
        robot_map = img
        # Image.frombuffer('L',  (map_width, map_height), img, 'raw', 'L', 0, 1).show()

        # robot_map = cv2.resize(img, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
        self.robot_map = robot_map
        self.resolution = resolution
        self.offset_x = offset_x
        self.offset_y = offset_y
        print("[INFO]: Showing the map")
        return resolution, offset_x, offset_y
        # if on_robot:
        #     # TODO: It requires a HTTPS server running. This should be somehow automated.
        #     cv2.imwrite(os.path.join(tmp_path, "map.png"), robot_map)
        #     # self.show_web(remote_ip + ":8000/map.png")
        #     # print("[INFO]: Map is available at: " + str(remote_ip) + ":8000/map.png")
        # else:
        #     print("this")
        #     cv2.imshow("RobotMap", robot_map)
        #     cv2.setMouseCallback("RobotMap", self.mouse_callback)
        #     # self.map_x, self.map_y, self.map_width, self.map_height = cv2.selectROI("robot_map", robot_map, False)
        #     # print(self.map_x, self.map_y, self.map_width, self.map_height)
        #     cv2.waitKey(0)
        #     cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flags, param):
        # 마우스 왼쪽 버튼을 클릭할 때
        self.map_x = x
        self.map_y = y
        if event == cv2.EVENT_LBUTTONDOWN:
            print("마우스 좌클릭:", self.map_x, self.map_y)

    def get_map(self, on_robot=False, remote_ip="lcoalhost"):
        """
        Shows a map from robot based on previously loaded one
        or explicit exploration of the scene. It can be viewed on
        the robot or in the computer by OpenCV.

        :param on_robot: If set shows a map on the robot
        :type on_robot: bool
        :param remote_ip: IP address of remote (default None)
        :type remote_ip: string

        .. warning:: Showing map on the robot is not fully supported at the moment.
        """
        result_map = self.navigation_service.getMetricalMap()
        map_width = result_map[1]
        map_height = result_map[2]
        img = numpy.array(result_map[4]).reshape(map_width, map_height)
        img = (100 - img) * 2.55  # from 0..100 to 255..0
        img = numpy.array(img, numpy.uint8)

        resolution = result_map[0]

        self.robot_localization()

        offset_x = result_map[3][0]
        offset_y = result_map[3][1]
        x = self.localization[0]
        y = self.localization[1]

        goal_x = (x - offset_x) / resolution
        goal_y = -1 * (y - offset_y) / resolution
        # path = self.navigation_service.getExplorationPath()
        # for i in path:
        #     print(i)
        #     path_x = (i[0] - offset_x) / resolution
        #     path_y = -1 * (i[1] - offset_y) / resolution
        #     img = cv2.circle(img, (int(path_x), int(path_y)), 1, (0, 255, 0), -1)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        cv2.circle(img, (int(goal_x), int(goal_y)), 3, (0, 0, 255), -1)

        robot_map = cv2.resize(img, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)

        return robot_map


    #load 맵 이후 첫 번째 localization할 때 사용
    def first_localization(self):
        try:
            self.navigation_service.relocalizeInMap([0., 0.])    
            self.navigation_service.startLocalization()
            a =time.sleep(3)
            print(a)

            self.navigation_service.navigateToInMap([2., 0., 0.])
            # self.motion_service.move(0,0,1)

            localization = self.navigation_service.getRobotPositionInMap()
            # exploration_path = self.navigation_service.getExplorationPath()
            self.localization_first = localization[0]
            self.localization_first2 = localization[1]

            print("localization", self.localization_first)

            print("[INFO]: Localization complete")

        except Exception as error:
            print(error)
            print("[ERROR]: Localization failed")

    
    def robot_localization(self):
        """
        Localize a robot in a map

        .. note:: After loading a map into robot or after new exploration \
        robots always need to run a self localization. Even some movement in \
        cartesian space demands localization.
        """
        # TODO: There should be localizeInMap() with proper coordinates

        try:
            self.navigation_service.startLocalization()
            # self.navigation_service.relocalizeInMap()

            # self.navigation_service.navigateToInMap([2., 0., 0.])
            localization = self.navigation_service.getRobotPositionInMap()
            # exploration_path = self.navigation_service.getExplorationPath()
            self.localization = localization[0]
            self.localization2 = localization[1]

            print("localization", self.localization)
            print("[INFO]: Localization complete")

            self.navigation_service.stopLocalization()
        except Exception as error:
            print(error)
            print("[ERROR]: Localization failed")


    def stop_localization(self):
        """Stop localization of the robot"""
        self.navigation_service.stopLocalization()
        print("[INFO]: Localization stopped")

    def load_map(self, file_name, file_path="/home/nao/.local/share/Explorer/"):
        """
        Load stored map on a robot. It will find a map in default location,
        in other cases alternative path can be specifies by `file_name`.

        .. note:: Default path of stored maps is `/home/nao/.local/share/Explorer/`

        .. warning:: If file path is specified it is needed to have `\` at the end.

        :param file_name: Name of the map
        :type file_name: string
        :param file_path: Path to the map
        :type file_path: string
        """
        # path = os.getcwd()
        # print("map file path:"+ path+ file_path + file_name)
        # image = cv2.imread(path+file_path+file_name)
        # print(image)
        try:
            self.slam_map = self.navigation_service.loadExploration(file_path+file_name)
            print("[INFO]: Map '" + file_name + "' loaded")
            print("load Map:", self.slam_map)    
        except:
            print("load Map error")
    def subscribe_camera(self, camera, resolution, fps):
        """
        Subscribe to a camera service. You need to subscribe a camera
        before you reach a images from it. If you choose `depth_camera`
        only 320x240 resolution is enabled.

        .. warning:: Each subscription has to have a unique name \
        otherwise it will conflict it and you will not be able to \
        get any images due to return value None from stream.

        :Example:

        >>> pepper.subscribe_camera(0, 1, 15)
        >>> image = pepper.get_camera_frame(False)
        >>> pepper.unsubscribe_camera()

        :param camera: `camera_depth`, `camera_top` or `camera_bottom`
        :type camera: string
        :param resolution:
            0. 160x120
            1. 320x240
            2. 640x480
            3. 1280x960
        :type resolution: integer
        :param fps: Frames per sec (5, 10, 15 or 30)
        :type fps: integer
        """
        color_space = 13

        camera_index = None
        if camera == "camera_top":
            camera_index = 0
        elif camera == "camera_bottom":
            camera_index = 1
        elif camera == "camera_depth":
            camera_index = 2
            resolution = 1
            color_space = 11
        
        self.camera_link = self.camera_device.subscribeCamera("Camera_Stream" + str(numpy.random.random()),
                                                              camera_index, resolution, color_space, fps)
        if self.camera_link:
            print("[INFO]: Camera is initialized")
        else:
            print("[ERROR]: Camera is not initialized properly")

    def unsubscribe_camera(self):
        """Unsubscribe to camera after you don't need it"""
        self.camera_device.unsubscribe(self.camera_link)
        print("[INFO]: Camera was unsubscribed")

    def get_camera_frame(self, show):
        """
        Get camera frame from subscribed camera link.

        .. warning:: Please subscribe to camera before getting a camera frame. After \
        you don't need it unsubscribe it.

        :param show: Show image when recieved and wait for `ESC`
        :type show: bool
        :return: image
        :rtype: cv2 image
        """
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)

        if show:
            cv2.imshow("Pepper Camera", image)
            cv2.waitKey(-1)
            cv2.destroyAllWindows()

        return image

    def get_depth_frame(self, show):
        """
        Get depth frame from subscribed camera link.

        .. warning:: Please subscribe to camera before getting a camera frame. After \
        you don't need it unsubscribe it.

        :param show: Show image when recieved and wait for `ESC`
        :type show: bool
        :return: image
        :rtype: cv2 image
        """
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)

        if show:
            cv2.imshow("Pepper Camera", image)
            cv2.waitKey(-1)
            cv2.destroyAllWindows()

        return image

    def show_tablet_camera(self, text):
        """
        Show image from camera with SpeechToText annotation on the robot tablet

        .. note:: For showing image on robot you will need to share a location via HTTPS and \
        save the image to ./tmp_pepper.

        .. warning:: It has to be some camera subscribed and ./tmp folder in root directory \
        exists for showing it on the robot.

        :Example:

        >>> pepper = Pepper("10.37.1.227")
        >>> pepper.share_localhost("/Users/michael/Desktop/Pepper/tmp_pepper/")
        >>> pepper.subscribe_camera("camera_top", 2, 30)
        >>> while True:
        >>>     pepper.show_tablet_camera("camera top")
        >>>     pepper.tablet_show_web("http://10.37.2.241:8000/tmp_pepper/camera.png")

        :param text: Question of the visual question answering
        :type text: string
        """
        remote_ip = socket.gethostbyname(socket.gethostname())
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)
        image = cv2.resize(image, (800, 600))
        cv2.putText(image, "Visual question answering", (30, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(image, "Question: " + text, (30, 550), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imwrite(os.path.join(tmp_path, "camera.png"), image)

        self.show_web("http://" + remote_ip + ":8000/%s" % os.path.join(tmp_path, "camera.png"))

    def navigate_to(self, x, y):
        """
        Navigate robot in map based on exploration mode
        or load previously mapped enviroment.

        .. note:: Before navigation you have to run localization of the robot.

        .. warning:: Navigation to 2D point work only up to 3 meters from robot.

        :Example:

        >>> pepper.robot_localization()
        >>> pepper.navigate_to(1.0, 0.3)

        :param x: X axis in meters
        :type x: float
        :param y: Y axis in meters
        :type y: float
        """
        print("[INFO]: Trying to navigate into specified location")
        try:
            self.navigation_service.startLocalization()
            # self.navigation_service.navigateToInMap(x, y)
            pos =self.navigation_service.getRobotPositionInMap()
            pos2 = pos[0]
            self.navigation_service.navigateToInMap([x, y, 0])


            print("robot_pos: " ,pos)
            self.pos = pos

            self.navigation_service.stopLocalization()
            print("[INFO]: Successfully got into location(navigation_move)")
            self.say("Arrived at destination")
        except Exception as error:
            print(error)
            print("[ERROR]: Failed to got into location(navigation_move)")
            self.say("I cannot move in that direction")
        
    def unsubscribe_effector(self):
        """
        Unsubscribe a end-effector after tracking some object

        .. note:: It has to be done right after each tracking by hands.
        """
        self.tracker_service.unregisterAllTargets()
        self.tracker_service.setEffector("None")
        print("[INFO]: End-effector is unsubscribed")

    def learn_face(self, name):
        """
        Tries to learn the face with the provided name.
        :param name:str, name to learn with face
        :return: str, name of human
        """
        self.set_awareness(True)
        # self.human_reco.subscribe_2reco()
        print("Waiting to see a human...")
        success = self.human_reco.learnFace(str(name))
        return success

    def recognize_person(self):
        """
        Tries to recognize the name of the person in front of Pepper
        :return: str, name of human
        """
        self.set_awareness(True)
        self.human_reco.subscribe_2reco()
        print("Waiting to see a human...")
        while not self.human_reco.human_name:
            pass
        name = self.human_reco.human_name if self.human_reco.human_name != "noone" else None
        return name

    def pick_a_volunteer(self):
        """
        Complex movement for choosing a random people.

        If robot does not see any person it will automatically after several
        seconds turning in one direction and looking for a human. When it detects
        a face it will says 'I found a volunteer' and raise a hand toward
        her/him and move forward. Then it get's into a default 'StandInit'
        pose.

        :Example:

        >>> pepper.pick_a_volunteer()

        """
        volunteer_found = False
        self.unsubscribe_effector()
        self.stand()
        self.say("I need a volunteer.")

        proxy_name = "FaceDetection" + str(numpy.random)

        print("[INFO]: Pick a volunteer mode started")

        while not volunteer_found:
            wait = numpy.random.randint(500, 1500) / 1000
            theta = numpy.random.randint(-10, 10)
            self.turn_around(theta)
            time.sleep(wait)
            # self.stop_moving()
            self.stand()
            try:
                self.face_detection_service.subscribe(proxy_name, 500, 0.0)
            except:
                print("face_detection_error")
            for memory in range(5):
                time.sleep(0.5)
                output = self.memory_service.getData("FaceDetected")
                print("...")
                if output and isinstance(output, list) and len(output) >= 2:
                    print("Face detected")
                    volunteer_found = True

        self.say("I found a volunteer! It is you!")
        self.stand()
        try:
            self.tracker_service.registerTarget("Face", 0.15)
            self.tracker_service.setMode("Move")
            self.tracker_service.track("Face")
            self.tracker_service.setEffector("RArm")
            self.get_face_properties()

        finally:
            time.sleep(2)
            self.unsubscribe_effector()
            self.stand()
            self.face_detection_service.unsubscribe(proxy_name)

    @staticmethod
    def share_localhost(folder):
        """
        Shares a location on localhost via HTTPS to Pepper be
        able to reach it by subscribing to IP address of this
        computer.

        :Example:

        >>> pepper.share_localhost("/Users/pepper/Desktop/web/")

        :param folder: Root folder to share
        :type folder: string
        """
        # TODO: Add some elegant method to kill a port if previously opened
        subprocess.Popen(["cd", folder])
        try:
            subprocess.Popen(["python", "-m", "SimpleHTTPServer"])
        except Exception as error:
            subprocess.Popen(["python", "-m", "SimpleHTTPServer"])
        print("[INFO]: HTTPS server successfully started")

    def play_sound(self, sound):
        """
        Play a `mp3` or `wav` sound stored on Pepper

        .. note:: This is working only for songs stored in robot.

        :param sound: Absolute path to the sound
        :type sound: string
        """
        print("[INFO]: Playing " + sound)
        self.audio_service.playFile(sound)

    def stop_sound(self):
        """Stop sound"""
        print("[INFO]: Stop playing the sound")
        self.audio_service.stopAll()

    def get_face_properties(self):
        """
        Gets all face properties from the tracked face in front of
        the robot.

        It tracks:
        - Emotions (neutral, happy, surprised, angry and sad
        - Age
        - Gender

        .. note:: It also have a feature that it substracts a 5 year if it talks to a female.

        .. note:: If it cannot decide which gender the user is, it just greets her/him as "Hello human being"

        ..warning:: To get this feature working `ALAutonomousLife` process is needed. In this methods it is \
        called by default
        """
        self.autonomous_life_on()
        emotions = ["neutral", "happy", "surprised", "angry", "sad"]
        face_id = self.memory_service.getData("PeoplePerception/PeopleList")
        recognized = None
        try:
            recognized = self.face_characteristic.analyzeFaceCharacteristics(face_id[0])
        except Exception as error:
            print("[ERROR]: Cannot find a face to analyze.")
            self.say("I cannot recognize a face.")

        if recognized:
            properties = self.memory_service.getData("PeoplePerception/Person/" + str(face_id[0]) + "/ExpressionProperties")
            gender = self.memory_service.getData("PeoplePerception/Person/" + str(face_id[0]) + "/GenderProperties")
            age = self.memory_service.getData("PeoplePerception/Person/" + str(face_id[0]) + "/AgeProperties")

            # Gender properties
            if gender[1] > 0.4:
                if gender[0] == 0:
                    self.say("Hello lady!")
                elif gender[0] == 1:
                    self.say("Hello sir!")
            else:
                self.say("Hello human being!")

            # Age properties
            if gender[1] == 1:
                self.say("You are " + str(int(age[0])) + " years old.")
            else:
                self.say("You look like " + str(int(age[0])) + " oops, I mean " + str(int(age[0]-5)))

            # Emotion properties
            emotion_index = (properties.index(max(properties)))

            if emotion_index > 0.5:
                self.say("I am quite sure your mood is " + emotions[emotion_index])
            else:
                self.say("I guess your mood is " + emotions[emotion_index])

    def listen_to(self, vocabulary, language="En"):
        """
        Listen and match the vocabulary which is passed as parameter.

        :Example:

        >>> words = pepper.listen_to(["what color is the sky", "yes", "no"]

        :param vocabulary: List of phrases or words to recognize
        :type vocabulary: list
        :return: Recognized phrase or words
        :rtype: string
        """
        self.speech_service.pause(True)
        if language == "En":
            self.speech_service.setLanguage("English")
        self.speech_service.removeAllContext()
        self.speech_service.deleteAllContexts()
        try:
            self.speech_service.setVocabulary(vocabulary,False)
        except:
            try:
                self.speech_service.subscribe("Test_ASR")
                self.speech_service.setVocabulary(vocabulary, False)
            except:
                self.speech_service.unsubscribe("Test_ASR")
                self.speech_service.setVocabulary(vocabulary, False)
        self.speech_service.subscribe("Test_ASR")
        print("[INFO]: Robot is listening to you...")
        self.speech_service.pause(False)
        time.sleep(4)
        words = self.memory_service.getData("WordRecognized")
        print("[INFO]: Robot understood: '" + words[0] + "'")
        self.speech_service.unsubscribe("Test_ASR")
        return words

    def listen(self, lang):
        """
        DOES NOT WORK WITHOUT LICENSE (that is our case :( )
        Wildcard speech recognition via internal Pepper engine

        .. warning:: To get this proper working it is needed to disable or uninstall \
        all application which can modify a vocabulary in a Pepper.

        .. note:: Note this version only rely on time but not its internal speak processing \
        this means that Pepper will 'bip' at the begining and the end of human speak \
        but it is not taken a sound in between the beeps. Search for 'Robot is listening to \
        you ... sentence in log console

        :Example:

        >>> words = pepper.listen()

        :return: Speech to text
        :rtype: string
        """
        self.speech_service.setAudioExpression(False)
        self.speech_service.setVisualExpression(False)
        self.audio_recorder.stopMicrophonesRecording()
        print("[INFO]: Speech recognition is in progress. Say something.")
        while True:
            print(self.memory_service.getData("ALSpeechRecognition/Status"))
            if self.memory_service.getData("ALSpeechRecognition/Status") == "SpeechDetected":
                self.audio_recorder.startMicrophonesRecording("/home/nao/speech.wav", "wav", 48000, (0, 0, 1, 0))
                print("[INFO]: Robot is listening to you")
                self.blink_eyes([255, 255, 0])
                break

        while True:
            if self.memory_service.getData("ALSpeechRecognition/Status") == "EndOfProcess":
                self.audio_recorder.stopMicrophonesRecording()
                print("[INFO]: Robot is not listening to you")
                self.blink_eyes([0, 0, 0])
                break

        self.download_file("speech.wav")
        self.speech_service.setAudioExpression(True)
        self.speech_service.setVisualExpression(True)

        return self.speech_to_text("speech.wav", lang)

    def ask_wikipedia(self):
        """
        Ask for question and then robot will say first two sentences from Wikipedia

        ..warning:: Autonomous life has to be turned on to process audio
        """
        self.speech_service.setAudioExpression(False)
        self.speech_service.setVisualExpression(False)
        self.set_awareness(False)
        self.say("Give me a question")
        question = self.listen()
        self.say("I will tell you")
        answer = tools.get_knowledge(question)
        self.say(answer)
        self.set_awareness(True)
        self.speech_service.setAudioExpression(True)
        self.speech_service.setVisualExpression(True)

    def rename_robot(self):
        """Change current name of the robot"""
        choice = raw_input("Are you sure you would like to rename a robot? (yes/no)\n")
        if choice == "yes":
            new_name = raw_input("Enter a new name for the robot. Then it will reboot itself.\nName: ")
            self.system_service.setRobotName(new_name)
            self.restart_robot()

    def upload_file(self, file_name):
        """
        Upload file to the home directory of the robot

        :param file_name: File name with extension (or path)
        :type file_name: string
        """
        self.scp.put(file_name)
        print("[INFO]: File " + file_name + " uploaded")
        self.scp.close()

    def download_file(self, file_name):
        """
        Download a file from robot to ./tmp folder in root.

        ..warning:: Folder ./tmp has to exist!
        :param file_name: File name with extension (or path)
        :type file_name: string
        """
        self.scp.get(file_name, local_path=tmp_path)
        print("[INFO]: File " + file_name + " downloaded")
        self.scp.close()

    def speech_to_text(self, audio_file, lang="en-US"):
        """
        Translate speech to text via Google Speech API

        :param audio_file: Name of the audio (default `speech.wav`)
        :param lang: Code of the language (e.g. "en-US", "cs-CZ")
        :type audio_file: string
        :return: Text of the speech
        :rtype: string
        """
        audio_file = sr.AudioFile(os.path.join(tmp_path, audio_file))
        with audio_file as source:
            audio = self.recognizer.record(source)
            recognized = self.recognizer.recognize_google(audio, language=lang)
        return recognized

    def chatbot(self):
        """
        Run chatbot with text to speech and speech to text

        ..warning:: This is not currently working
        """
    
        while True:
            try:
                self.set_awareness(False)
                # question = self.listen()
                question = "sdasdf"
                print("[USER]: " + question)
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": "You are name is pepper"},
                {"role": "user", "content": question}]

                response = openai.ChatCompletion.create(
                model=model,
                messages=messages
                )
                answer = response['choices'][0]['message']['content']
                print("[ROBOT]: "+ answer)
                self.say(answer)
            except KeyboardInterrupt:
                self.set_awareness(True)

    def streamCamera(self):
        self.subscribe_camera("camera_top", 2, 30)

        while True:
            image = self.get_camera_frame(show=False)
            cv2.imshow("frame", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.unsubscribe_camera()
        cv2.destroyAllWindows()

    def recognize_google(self, lang):
        """
        Uses external SpeechRecognition library to transcribe speech to text. The sound is first recorded into .wav file and then analysed with Google cloud service.
        :param lang: str
        """
        self.recordSound()
        return self.speech_to_text("speech.wav", lang)

    def recordSound(self):
        try:
            self.audio_recorder.stopMicrophonesRecording()
        except:
            pass
        print ("start recording")
        self.audio_recorder.startMicrophonesRecording("/home/nao/speech.wav", "wav", 48000, (0, 0, 1, 0))
        time.sleep(5)
        self.audio_recorder.stopMicrophonesRecording()
        print ("record over")
        self.download_file("speech.wav")

    def changeVoice(self, volume, speed, shape):
        self.set_volume(volume)
        self.voice_speed = speed
        self.voice_shape = shape
        language = self.dialog_service.getLanguage()
        if language == "Czech":
            self.say("Zkouška hlasu")
        elif language == "English":
            self.say("Sound check")
        

    def set_awareness(self, on=True):
        """
        Turn on or off the basic awareness of the robot,
        e.g. looking for humans, self movements etc.

        :param state: If True set on, if False set off
        :type state: bool
        """
        if on is True:
            self.awareness_service.resumeAwareness()
            print("[INFO]: Awareness is turned on")
        else:
            self.awareness_service.pauseAwareness()
            print("[INFO]: Awareness is paused")

    def move_forward(self, speed):
        """
        Move forward with certain speed
        :param speed: Positive values forward, negative backwards
        :type speed: float
        """
        self.motion_service.move(speed, 0, 0)

    def set_security_distance(self, distance=0.05):
        """
        Set security distance. Lower distance for passing doors etc.

        .. warning:: It is not wise to turn `security distance` off.\
        Robot may fall from stairs or bump into any fragile objects.

        :Example:

        >>> pepper.set_security_distance(0.01)

        :param distance: Distance from the objects in meters
        :type distance: float
        """
        # self.motion_service.setExternalCollisionProtectionEnabled("All", True)
        self.motion_service.setOrthogonalSecurityDistance(distance)
        print("[INFO]: Security distance set to " + str(distance) + " m")

    def move_head_down(self):
        """Look down"""
        self.motion_service.setAngles("HeadPitch", 0.46, 0.2)

    def move_head_up(self):
        """Look up"""
        self.motion_service.setAngles("HeadPitch", -0.4, 0.2)

    def move_head_default(self):
        """Put head into default position in 'StandInit' pose"""
        self.motion_service.setAngles("HeadPitch", 0.0, 0.2)

    def move_to_circle(self, clockwise, t=10):
        """
        Move a robot into circle for specified time

        .. note:: This example only count on time not finished circles.

        >>> pepper.move_to_circle(clockwise=True, t=5)

        :param clockwise: Specifies a direction to turn around
        :type clockwise: bool
        :param t: Time in seconds (default 10)
        :type t: float
        """
        if clockwise:
            self.motion_service.moveToward(0.5, 0.0, 0.6)
        else:
            self.motion_service.moveToward(0.5, 0.0, -0.6)
        time.sleep(t)
        self.motion_service.stopMove()

    def move_joint_by_angle(self, joints, angles, fractionMaxSpeed=0.2, blocking=False):
        """
        :param joints: list of joint types to be moved according to http://doc.aldebaran.com/2-0/_images/juliet_joints.png
        :param angles: list of angles for each joint
        :param fractionMaxSpeed: fraction of the maximum speed for joint motion, i.e. an integer (0-1)
        """
        #self.motion_service.setStiffnesses("Head", 1.0)
        # Example showing how to set angles, using a fraction of max speed
        self.motion_service.setAngles(joints, angles, fractionMaxSpeed)
        
        # TODO: zmena dist
        
        if blocking:
            epsilon = 0.12
            last_angles = [-100]*len(joints)
            while True:
                time.sleep(0.1)
                now_angles = self.motion_service.getAngles(joints, True)
                dist = 0
                change = 0
                for i in range(len(joints)):
                    dist += (now_angles[i]-angles[i])**2
                    change += abs(now_angles[i]-last_angles[i])
                last_angles = [angle for angle in now_angles]
                #print("change", change)
                if dist < 0.15 and change < 0.005:
                    #print("konec", dist)
                    break
        
        #    print()
            #self.motion_service.angleInterpolation(joints, angles, len(joints)*[end_time], True);
        #time.sleep(3.0)
        #motion_service.setStiffnesses("Head", 0.0)

    def do_hand_shake(self):
        self.move_joint_by_angle(["RElbowRoll", "RShoulderPitch", "RElbowYaw", "RWristYaw"], [1, 1, 1, 1], 1.0)
        self.hand("right", False)
        time.sleep(3)
        self.hand("right", True)
        self.move_joint_by_angle(["RElbowRoll", "RShoulderPitch", "RElbowYaw", "RWristYaw"], [0, 1.5, 1, 1], 1.0)



def main():
    pepper = RosKuPepper(rospy.get_param('~pepper_ip'), rospy.get_param('~pepper_port'))
    # pepper = RosKuPepper("192.168.214.51", "9559")
    pepper.talker()


if __name__ == "__main__":
    rospy.init_node('talker', anonymous=True)

    base_thread = threading.Thread(target=main)
    base_thread.daemon = True
    base_thread.start()

    app.run(host=web_host, port=8080, debug=False)
    
    # thread = threading.Thread(target=pepper.base)
    # thread.start()


    



