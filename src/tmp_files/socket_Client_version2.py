# -*- coding: utf-8 -*-

import json
import openai
import socket, threading
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored  
import sys
GPT_MODEL = "gpt-3.5-turbo"
client = OpenAI(api_key='')

# server_ip = '192.168.122.56'
server_ip = sys.argv[1]
server_port = 3333 

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((server_ip, server_port))

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print("Exception: {}".format(e))
        return e
    
tools = [
     {
        "type": "function",
        "function": {
            "name": "pepper_location",
            "description": "누군가의 위치를 물어본다면",
            "parameters": {
                "type": "object",
                "properties": {
                    "위치요구": {
                        "type": "string",
                            "description": "요구 위치 저장.",
                    },
                },

            "required": ["위치요구"]
            
            },
        }
    },
       {
        "type": "function",
        "function": {
            "name": "pepper_navigation",
            "description": "장소로 안내를 원한다면",
            "parameters": {
                "type": "object",
                "properties": {
                    "안내요구": {
                        "type": "string",
                            "enum": ["안내 필요 없음", "위치만 필요", "직접 안내 필요"],
                            "description": "질문자의 의도 파악 후 셋 중 하나 선택.",
                    },
                },

            "required": ["안내요구"]
            
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pepper_behavior",
            "description": "페퍼가 무엇인가 행동하기를 원한다면",
            "parameters": {
                "type": "object",
                "properties": {
                    "행동": {
                        "type": "string",
                            "enum": ["춤 추기", "박수 치기", "가위바위보 하기", "행동 그만하기"],
                            "description": "질문자의 의도 파악 후 셋 중 하나 선택.",
                    },
                },

            "required": ["행동"]
            
            },
        }
    },
        {
        "type": "function",
        "function": {
            "name": "pepper_mood",
            "description": "정서에 대해서 질문할 때만.",
            "parameters": {
                "type": "object",
                "properties": {
                    "감정": {
                        "type": "string",
                            "enum": ["웃기", "화내기", "슬퍼하기"],
                            "description": "질문자의 의도 파악 후 셋 중 하나 선택.",
                    },
                },

            "required": ["감정"]
            
            },
        }
    },
]


count = 0
messages = [{"role": "system","content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."},
            {"role": "system", "content": "니 이름은 pepper(페퍼)이고 너는 경남대학교 1공학관 8층에 위치해있다. 너는 텍스트 기반 챗봇이 아니다."},#""이걸로 줄 바꿔도 한줄로 인식 가능
            {"role": "system", "content": "답변할 때 무조건 줄 띄우지 말고 한 문단으로 답변해 줘."},
            
            {"role": "system", "content": "8층에는 pbl실,교수연구실,임베디드실습실등이 있다."},
            {"role": "system", "content": "넌 경남대학교 8층의 안내로봇이야. 말을 할 때 무조건 존댓말로 해야해"},
            {"role": "system", "content": "8층의 화장실은 두 곳으로 한 곳은 엘리베이터 뒤쪽, 다른 한 곳은 컴퓨터네트워크 실습준비실과 자바OS 실습실 사이에 위치해있다."},

            
            {"role": "system", "content": "1공학관 8층엔 임베디드응용 소프트웨어 실습실, 801강의실, 802강의실등 총 16개의 강의실이 있다. "},
            {"role": "system", "content": "1공학관 8층엔 전하용, 임지언, 서쌍희 등 총 13명의 교수연구실이 있다."},
            
            #왼쪽 벽면
            {"role": "system", "content": "1공학관 8층의 방 구조는 엘리베이터를 기준으로 왼쪽 벽면, 위쪽 벽면,  오른쪽 벽면, 아래쪽 벽면으로 설명하면 된다. 엘리베이터가 첫 번째 모퉁이에 위치하고, 왼쪽 벽면과 위쪽 벽면이 만나는 두 번째 모퉁이엔 융합 인공지능 실습실, 위쪽 벽면과 오른쪽 벽면이 만나는 세 번째 모퉁이엔 미래인터넷 실습실, 오른쪽 벽면과 아랫쪽 벽면이 만나는 네 번째 모퉁이엔 803 강의실, 아래쪽 벽면과 왼쪽 벽면이 만나는 첫 번째 모퉁이엔 엘리베이터가 있다."},
            {"role": "system", "content": "엘리베이터 뒤엔 첫 번째 화장실이 위치한다. 화장실 맞은편엔 전하용 교수연구실이 있다. 화장실의 왼쪽엔 컴퓨터공학부 사무실, 화장실 오른쪽엔 엘리베이터가 있고 화장실 맞은편엔 전하용 교수연구실이 있다."},
            {"role": "assistant", "content": "엘리베이터는 8층의 첫 번째 모퉁이에 위치하고, 엘리베이터를 기준점으로 8층 건물의 왼쪽 벽면엔 1. 전하용 교수연구실 2. 임지언 교수연구실 3. 실시간 시스템 통계분석 자료실습실 4. 서쌍희 교수연구실 5. 시스템분석 실습실 6. 인터넷 데이터베이스 실습실 7. 황두영 교수연구실 8. 801강의실 9. 융합 인공지능 실습실 이 1~9번의 순서로 방들이 위치해있다. "},

            {"role": "assistant", "content": "예를 들어 801강의실이 어디냐 묻는다면 \"801강의실은 황두영 교수연구실 옆에 있습니다.\" 라고 알려줘야한다."},
            {"role": "system", "content": "융합 인공지능 실습실은 8층 두 번째 모퉁이이고 801강의실과 석승준 교수연구실 사이에 있다."},

            #위쪽 벽면
            {"role": "assistant", "content": "엘리베이터를 기준으로 8층 건물의 위쪽 벽면은 1. 융합 인공지능 실습실 2. 석승준 교수연구실 3. 임현일 교수연구실 4. 정민수 교수연구실 5. 김진호 교수연구실 6. 양근석 교수연구실 7. 하경재 교수연구실 이 순서로 위치해있다."},
            {"role": "assistant", "content": "정민수 교수연구실이 어디냐 물어보면 \"정민수 교수연구실은 김진호 교수연구실과 임현일 교수연구실 사이에 위치해있습니다.\" 이런식으로 위치를 알려줘야한다."},
            {"role": "system", "content": "미래인터넷 실습실은 8층의 세 번째 모퉁이에 있으며 미래인터넷 실습실 오른쪽엔 하경재 교수연구실, 미래인터넷 실습실 왼쪽엔 박미영 교수연구실이 있다."},

            #오른쪽 벽면
            {"role": "assistant", "content": "엘리베이터를 기준으로 8층 건물의 오른쪽 벽면은 1. 미래인터넷 실습실 2. 박미영 교수연구실 3. 소프트웨어 및 정보보안PBL실 4. 컴퓨터공학PBL실 5. 컴퓨터 응용실습실 6. 컴퓨터응용 실습준비실 7. 홈네트워크실습실 8. 803강의실 이 순서로 위치해있다."},
            {"role": "assistant", "content": "박미영 교수연구실이 어디내 물어보면 \"박미영 교수연구실은 미래인터넷 실습실과 소프트웨어 및 정보보안PBL실 사이에 위치해있습니다.\" 이런식으로 위치를 알려줘야한다."},
            {"role": "assistant", "content": "모퉁이에 위치한 장소를 알려줄때, 예를 들어 미래인터넷 실습실이 어디냐 물어보면 \"미래인터넷 실습실은 박미영 교수연구실 옆에 위치해있습니다.\" 이런식으로 옆에 있는 방 정보를 함께 알려줘야한다."},

            #아래쪽 벽면
            {"role": "assistant", "content": "엘리베이터를 기준으로 아래쪽 벽면엔 1. 803강의실 2. 802강의실 3. 임베디드응용 소프트웨어실습실 이 순서로 위치해있다."},
            
            #엘베 왼쪽 복도 기준 오른쪽 벽면
            {"role": "system", "content": "엘리베이터 왼쪽 복도에서 오른쪽 벽면엔 1. 화장실(전하용 교수연구실 맞은편) 2. 컴퓨터공학부 사무실(임지언 교수연구실 맞은편) 3. 이기성 교수연구실(실시간 시스템 통계분석 자료실습실 맞은편) 4. 이현동 교수연구실(서쌍희 교수연구실 맞은편) 5. 컴퓨터네트워크실습실(시스템분석 실습실 맞은편) 6. 컴퓨터네트워크 실습준비실(인터넷 데이터베이스 실습실 맞은편) 7. 화장실 이 순서로 위치해있다."},
            {"role": "system", "content": "자바OS 실습실은 임베디드시스템 실습실/캡스톤디자인실 옆에 위치해있고, 김진호 교수연구실 맞은편이다."},
            {"role": "system", "content": "임베디드시스템 실습실/캡스톤디자인실은 양근석 교수연구실과 하경재 교수연구실 맞은편에 위치해있다."},

            {"role": "assistant", "content": "중앙계단은 컴퓨터 응용실습실 맞은편에 위치해있다."},
            {"role": "system", "content": "function에 대한 내용이 부족하면 가정하지 말고 물어보기"},
            {"role": "system", "content": "페퍼는 가상이 아니며 실제로 이동할 수 있다. 누군가 이동을 원하면 그리로 이동할 수 있다."},
            ]

location = {"임지언": (300, 400), "김진호": (31.4435647013,7.18209944068)}
# messages = []
# messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})

def move(member):
    for i in location.keys():
        if i in member:
            print("move x: ", location.get(i)[0], "move y: ", location.get(i)[1])
            return "-FMG-navi_{}_{}".format(location.get(i)[0], location.get(i)[1])
    return "-FMG-None"
def dance():
    print("dance!!!!!!")
    return "-FMG-dance"

def clap():
    print("clap!!!!!!")
    return "-FMG-clap"
    

def rock_paper_scissors():
    print("rock_paper_scissors")
    return "-FMG-rock_paper_scissors"
    

def stop_behavior():
    print("stopstop!!")
    return "-FMG-stop_behavior"


def happy():
    return "-FMG-happy"
    

def sad():
    return "-FMG-sad"
    

def angry():
    return "-FMG-angry"
    

def nothing():
    return "-FMG-nothing"
    

member = ""

while True:
    chat_use = False
    data = socket.recv(1000)#메시지 받는 부분
    msg = data.decode() 
    send_message = ""
    messages.append({"role": "user", "content" : "{}".format(msg)})
    chat_response = chat_completion_request(
        messages=messages, tools=tools, tool_choice="auto"
    )
    assistant_message = chat_response.choices[0].message
    
    print("assistant_message:" , assistant_message.content)
    send_message += "-BMG-" + str(assistant_message.content)

    tool_calls = assistant_message.tool_calls
    print(tool_calls)


    
    if tool_calls:
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        print(tool_call_id,tool_function_name ,tool_calls[0].function.arguments)
        messages.append(assistant_message)
        messages.append(
        {
            "role": "tool",
            "tool_call_id":tool_call_id,
            "name": tool_function_name,
            "content": tool_calls[0].function.arguments,
        }
        ) 
        if tool_function_name == "pepper_location":
            messages.append({"role": "system", "content": "직접 안내가 필요하냐고 물어보기. 만약 안내해달라고 하면, 사족 덧붙이지 말고 \"안내해드릴게요\" 라고 말하기."})
            member = tool_calls[0].function.arguments
            chat_use = True
        elif tool_function_name == "pepper_navigation":
            if "직접 안내 필요" in tool_calls[0].function.arguments:
                print(tool_calls[0].function.arguments)
                send_message += str(move(member))
                chat_use = True
        elif tool_function_name == "pepper_behavior":
            if "춤 추기" in tool_calls[0].function.arguments:
                messages.append({"role": "system", "content": "\"춤을 한번 춰볼게요!\"라고 말한다. 춤을 못춘다고 절대 말하지 않는다."})
                send_message += dance()
                chat_use = True
            elif "박수 치기" in tool_calls[0].function.arguments:
                send_message += clap()
                chat_use = True
            elif "가위바위보 하기" in tool_calls[0].function.arguments:
                send_message += rock_paper_scissors()
                chat_use = True   
            elif "행동 그만하기" in tool_calls[0].function.arguments:
                send_message += stop_behavior()
                chat_use = True 

        elif tool_function_name == "pepper_mood":
            if "웃기" in tool_calls[0].function.arguments:
                send_message += happy()
            elif "화내기" in tool_calls[0].function.arguments:
                send_message += angry()   
            elif "슬퍼하기" in tool_calls[0].function.arguments:
                send_message += sad()   


        if chat_use == True:
            try:                                
                chat_response = chat_completion_request(
                    messages=messages, tools=None, tool_choice=None
                )
                assistant_message = chat_response.choices[0].message
                print("assistant_message:" , assistant_message.content)
                send_message += "-TMG-" + str(assistant_message.content)
                chat_use = False
            except:
                pass
        chat_use = False
    print(send_message)
    socket.sendall(send_message.encode(encoding='utf-8'))
    
    if msg == '/end':
        break
    count += 1 

