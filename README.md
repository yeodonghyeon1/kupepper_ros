# Pepper Robot ROS Integration Project 🤖

![스크린샷 2025-03-05 182143 - 복사본](https://github.com/user-attachments/assets/e32462bc-1650-4386-96bc-9bd12a0fa725)

## 프로젝트 개요

이 프로젝트는 Pepper 로봇을 ROS (Robot Operating System)와 통합하여 자율 주행, 네비게이션, 그리고 GPT 기반 대화 기능을 구현한 시스템입니다.

## 주요 기능 🎯

1. **자율 주행 시스템**
   - SLAM 기반 지도 생성 (gmapping)
   - AMCL 기반 위치 추정
   - 다중 레이저 스캔 데이터 통합
   - 깊이 이미지를 레이저 스캔으로 변환

2. **Pepper 로봇 제어**
   - NAOqi 드라이버 통합
   - MoveIt! 기반 모션 제어
   - 웹 인터페이스 기반 원격 제어

3. **GPT 통합**
   - ROS-GPT 인터페이스
   - 자연어 기반 로봇 제어
   - Flask 기반 웹 서버 통합

## 시스템 구조 📂

```
kupepper_ros/
├── config/       # 로봇 및 네비게이션 설정
├── launch/       # 실행 파일
│   ├── amcl_kupepper.launch    # 위치 추정
│   ├── cartographer.launch     # 지도 생성
│   ├── pepper_gmapping.launch  # SLAM
│   └── move_test.launch       # 이동 테스트
├── map/          # 생성된 맵 저장
├── rviz/         # 시각화 설정
├── src/          # 소스 코드
│   ├── flask_server.py       # 웹 서버
│   ├── rosgpt.py            # GPT 인터페이스
│   ├── moveit_test.py       # 모션 제어
│   └── main.py              # 메인 로직
└── yaml/         # 파라미터 설정

```

## 필수 패키지 및 의존성 📦

### ROS 패키지
```bash
# 네비게이션 스택
sudo apt install ros-melodic-navigation
sudo apt install ros-melodic-gmapping
sudo apt install ros-melodic-openslam-gmapping

# MoveIt!
sudo apt install ros-melodic-moveit

# 기타 의존성
sudo apt install ros-melodic-tf2-sensor-msgs
sudo apt install libsdl-image1.2-dev libsdl-dev
```

### Python 패키지
```bash
pip install flask
pip install openai
```

### 추가 의존성 패키지
```bash
cd ~/catkin_ws/src

# 깊이 이미지 변환
git clone https://github.com/ros-perception/depthimage_to_laserscan

# 레이저 스캔 통합
git clone https://github.com/iralabdisco/ira_laser_tools

# 네비게이션 메시지
git clone https://github.com/ros-planning/navigation_msgs.git
```

## 설치 방법 🔧

1. **PyNAOqi SDK 설치**
```bash
# Pepper SDK 2.5.5 다운로드 및 설치
wget https://community-static.aldebaran.com/resources/2.5.5/Python%20SDK/pynaoqi-python2.7-2.5.5.5-linux64.tar.gz
tar -xvzf pynaoqi-python2.7-2.5.5.5-linux64.tar.gz

# 환경변수 설정
echo "export PYTHONPATH=${PYTHONPATH}:~/pynaoqi/lib/python2.7/site-packages" >> ~/.bashrc
source ~/.bashrc
```

2. **워크스페이스 설정**
```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
git clone https://github.com/yeodonghyeon1/kupepper_ros.git
cd ..
catkin_make
source devel/setup.bash
```

## 실행 방법 🚀

1. **Pepper 연결 설정**
```bash
# Pepper 설정 실행
roslaunch kupepper_ros pepper_configuration.launch nao_ip:=<PEPPER_IP>
```

2. **SLAM 모드 (지도 생성)**
```bash
# SLAM 실행
roslaunch kupepper_ros pepper_gmapping.launch
```

3. **네비게이션 모드**
```bash
# 저장된 지도로 네비게이션
roslaunch kupepper_ros amcl_kupepper.launch
```

4. **웹 인터페이스 실행**
```bash
# Flask 서버 실행
rosrun kupepper_ros flask_server.py
```

## 주요 기능 사용법 💡

1. **지도 생성**
   - gmapping 또는 Cartographer 중 선택
   - RViz에서 실시간 지도 확인
   - 지도 저장: `rosrun map_server map_saver`

2. **자율 주행**
   - RViz에서 2D Nav Goal 설정
   - 웹 인터페이스에서 목적지 지정
   - GPT 명령어로 이동 지시

3. **로봇 제어**
   - MoveIt!을 통한 관절 제어
   - 웹 인터페이스를 통한 원격 조작
   - 음성 명령을 통한 제어

## 문제 해결 🔍

1. **NAOqi 드라이버 관련**
   - apt로 설치된 naoqi_driver와 소스 빌드 버전 충돌 시:
   ```bash
   sudo apt remove ros-melodic-naoqi-driver
   sudo apt install ros-melodic-naoqi-driver
   ```

2. **의존성 문제**
   - SDL 관련 에러:
   ```bash
   sudo apt-get install libsdl-image1.2-dev
   sudo apt-get install libsdl-dev
   ```

3. **네비게이션 문제**
   - 레이저 스캔 데이터 확인
   - TF 트리 구조 확인
   - 파라미터 튜닝


