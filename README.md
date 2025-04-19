# Pepper Robot ROS Integration Project 🤖

## 프로젝트 개요

이 프로젝트는 Pepper 로봇을 ROS (Robot Operating System)와 통합하여 자율 주행 및 네비게이션 기능을 구현한 시스템입니다.

## 주요 기능 🎯

1. **자율 주행 시스템**
   - SLAM을 통한 지도 생성
   - 네비게이션 및 장애물 회피
   - 깊이 이미지를 레이저 스캔으로 변환

2. **Pepper 로봇 제어**
   - NAOqi 드라이버 통합
   - 로봇 모션 제어
   - 센서 데이터 처리

3. **시각화 도구**
   - RViz 설정 및 시각화
   - 맵 데이터 표시
   - 센서 데이터 시각화

## 시스템 구조 📂

```
kupepper_ros/
├── config/       # 설정 파일
├── launch/       # 실행 파일
├── map/          # 맵 데이터
├── rviz/         # RViz 설정
├── src/          # 소스 코드
├── yaml/         # YAML 설정
└── yaml2/        # 추가 YAML 설정
```

## 설치 방법 🔧

### 필수 패키지 설치

```bash
# ROS 네비게이션 패키지
sudo apt install ros-melodic-navigation

# GMAPPING 패키지
sudo apt install ros-melodic-gmapping
sudo apt install ros-melodic-openslam_gmapping

# NAOqi 드라이버
sudo apt install ros-melodic-naoqi-driver
```

### 추가 의존성 패키지 (Git Clone 필요)

```bash
cd ~/catkin_ws/src

# Depth Image to Laser Scan
git clone https://github.com/ros-perception/depthimage_to_laserscan

# IRA Laser Tools
git clone https://github.com/iralabdisco/ira_laser_tools

# Navigation Messages (필요한 경우)
git clone https://github.com/ros-planning/navigation_msgs.git
```

### PyNAOqi SDK 설치

1. Pepper SDK 2.5.5 버전 다운로드
2. 압축 해제: `tar -zxvf pynaoqi-python2.7-2.5.5.5-linux64.tar.gz`
3. 환경변수 설정:
```bash
echo "export PYTHONPATH=${PYTHONPATH}:~/pynaoqi/lib/python2.7/site-packages" >> ~/.bashrc
source ~/.bashrc
```

## 실행 방법 🚀

1. ROS 마스터 실행
```bash
roscore
```

2. Pepper 로봇 연결
```bash
roslaunch pepper_bringup pepper_full.launch nao_ip:=<PEPPER_IP>
```

3. 네비게이션 실행
```bash
roslaunch pepper_navigation navigation.launch
```

## 문제 해결 🔍

### 일반적인 에러 해결 방법

1. SDL 관련 에러:
```bash
sudo apt-get install libsdl-image1.2-dev
sudo apt-get install libsdl-dev
```

2. tf2_sensor_msgs 에러:
```bash
sudo apt-get install ros-kinetic-tf2-sensor-msgs
```

3. NAOqi 드라이버 빌드 에러:
- apt로 설치된 naoqi_driver가 있는 경우 git clone 버전과 충돌 발생
- 해결: `sudo apt install ros-melodic-naoqi-driver` 사용

## 기여 방법 🤝

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

# introduce

_ros-medloic version ros pepper_

ㅎㅎㅎ

# require

> ## depthimage_to_laserscan(git clone)

https://github.com/ros-perception/depthimage_to_laserscan

> ## ira_laser_tools(git clone)

https://github.com/iralabdisco/ira_laser_tools

> ## ros_navigation(sudo apt install ros-melodic-navigation)

https://github.com/ros-planning/navigation

> ## ros_gmapping(sudo apt install ros-melodic-gmapping)

https://github.com/ros-perception/slam_gmapping

> ## ros_openslam gmapping(sudo apt install ros-melodic-openslam_gmapping)

https://github.com/ros-perception/openslam_gmapping

> ## naoqi_driver(git clone)

https://github.com/ros-naoqi/naoqi_driver

> ## pynaoqi(first install!! )

https://www.aldebaran.com/en/support/pepper-naoqi-2-9/downloads-softwares

1. download old:Pepper SDK(for2.5.5 ver)
2. tar -zxvf
3. export PYTJONPATH=${PYTHONPATH}:~/pynaoqi/lib/python2.7/site-packages # add at ~/.bashrc file, pynaoqi will be change for version!!!

# Error solution

Could NOT find SDL (missing: SDL_LIBRARY SDL_INCLUDE_DIR)

> sudo apt-get install libsdl-image1.2-dev sudo apt-get install libsdl-dev

Could not find a package configuration file provided by "tf2_sensor_msg

> sudo apt-get install ros-kinetic-tf2-sensor-msgs

CMake error with move_base_msgs

> git clone https://github.com/ros-planning/navigation_msgs.git

naoqi driver catkin_make Error if you already install naoqi_driver for apt, you can't catkin_make naoqi_driver(git clone)

> sudo apt install ros-melodic-naoqi-driver