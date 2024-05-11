import socket, time

host = '192.168.112.1' 
port = 3333 

# 서버소켓 오픈/ netstat -a로 포트 확인
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))

# 클라이언트 접속 준비 완료
server_socket.listen()

print('echo server start')

#  클라이언트 접속 기다리며 대기 
client_soc, addr = server_socket.accept()

print('connected client addr:', addr)

# 클라이언트가 보낸 패킷 계속 받아 에코메세지 돌려줌
while True:
    msg2 = input('msg:') 
    client_soc.sendall(msg2.encode(encoding='utf-8')) 
    data = client_soc.recv(1000)#메시지 받는 부분
    msg = data.decode() 
    print('recv msg:', msg)
    if msg == '/end':
        break

time.sleep(5)
print('서버 종료')
server_socket.close() # 사용했던 서버 소켓을 닫아줌
