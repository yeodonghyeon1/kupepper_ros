#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, time
import speech_recognition as sr

host = '172.23.28.1' 
port = 3333 

# 서버소켓 오픈/ netstat -a로 포트 확인
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))

# 클라이언트 접속 준비 완료
server_socket.listen(1)

print('echo server start')

#  클라이언트 접속 기다리며 대기 
client_soc, addr = server_socket.accept()

print('connected client addr:', addr)

r = sr.Recognizer()
kr_audio = sr.AudioFile('./pepper_test.wav')#파일 경로

with kr_audio as source:
    audio = r.record(source)

# 클라이언트가 보낸 패킷 계속 받아 에코메세지 돌려줌
while True:
    msg2 = r.recognize_google(audio, language='ko-KR')
    print(r.recognize_google(audio, language='ko-KR'))
    client_soc.sendall(msg2.encode(encoding='utf-8')) 
    data = client_soc.recv(1000)#메시지 받는 부분
    msg = data.decode("utf-8")
    split_msg = msg.split("-")
    print(split_msg[1])
    for i in split_msg:
        print(i)
    msg=input('/end입력시 종료 :')
    if msg == '/end':
        break

time.sleep(5)
print('서버 종료')
server_socket.close() # 사용했던 서버 소켓을 닫아줌