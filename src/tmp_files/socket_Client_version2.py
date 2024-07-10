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
#어떤 장소나 위치에 대해서 물어봤을 때 작동. 어딘지 묻거나, 어디냐고 묻는 등등의 질문에서 작동.
tools = [
     {
        "type": "function",
        "function": {
            "name": "pepper_location",
            "description": "어떤 장소나 위치를 물어보거나 알려달라고 한다면.",
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
            "description": "pepper_location 함수가 사용된 이후 장소로 안내를 원한다면",
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

    {
        "type": "function",
        "function": {
            "name": "pepper_action",
            "description": "페퍼에게 재미를 요구 하면",
            "parameters": {
                "type": "object",
                "properties": {
                    "재미": {
                        "type": "string",
                            "enum": ["기타치기", "좀비흉내내기", ""],
                            "description": "질문자의 의도 파악 후 셋 중 하나 선택.",
                    },
                },

            "required": ["재미"]

            },
        }
    },

        {
        "type": "function",
        "function": {
            "name": "faceage",
            "description": "페퍼에게 사용자의 나이를 물어보면",
            "parameters": {
                "type": "object",
                "properties": {
                    "나이": {
                        "type": "string",
                            "description": "",
                    },
                },

            "required": ["나이"]

            },
        }
    },
        {
        "type": "function",
        "function": {
            "name": "stop_navigation",
            "description": "페퍼한테 안내를 멈춰달라고 한다면",
            "parameters": {
                "type": "object",
                "properties": {
                    "멈추기": {
                        "type": "string",
                            "enum": ["안내 멈추기"],
                            "description": "안내 멈추기 반환",
                    },
                },

            "required": ["멈추기"]

            },
        }
    },
            {
        "type": "function",
        "function": {
            "name": "move",
            "description": "임의로 어느 방향으로 움직이길 원하면",
            "parameters": {
                "type": "object",
                "properties": {
                    "움직이기": {
                        "type": "string",
                            "enum": ["앞쪽, 왼쪽, 오른쪽, 뒤쪽, 랜덤"],
                            "description": "다섯 방향 중 한 곳 선택. 저리가 또는 비켜 등의 애매한 단어일 시 랜덤으로 반환.",
                    },
                },

            "required": ["움직이기"]

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

location = {"802": (7.41363859177,0.646141052246,-0.186690305871,0.982418815828), 
            "801": (18.3805084229,26.7191734314,-0.673472857532,0.739211952127), 
            "803": (-21.5854701996,-5.10018348694,0.102878790778,0.994693899855),
            "과학영재정보과학교실": (-21.5854701996,-5.10018348694,0.102878790778,0.994693899855),
            "컴퓨터응용실습준비실": (-13.0078125,-3.54687309265,0.0864883732686,0.996252860116),
            "USG현장미러형 실습실": (-11.0526866913,-3.02528548241,0.105992433122,0.994366936357),
            "컴퓨터공학PBL실": (-0.159409821033,-1.15033531189,0.12191808491,0.992540165722),
            "소프트웨어 및 정보보안 PBL실": (14.1229610443,1.01963496208,0.0369401701272,0.999317478998),
            "미래 인터넷 실습실": (31.8135185242,1.36800861359,0.722566403011,0.691301521219),
            "임베디드시스템실습실 캡스톤디자인실": (20.5724372864,1.04382514954,0.0339547197359,0.999423372254),
            "자바OS실습실": (19.0750846863,18.0170345306,0.039317849285,0.999226754409),
            "ABEEK자료 보관실": (29.4902420044,21.1318874359,0.0365514640859,0.999331771972),
            "컴퓨터 네트워크 실습준비실": (8.33035945892,27.9321670532,0.0803707754657,0.996765036732),
            "실시간시스템 통계분석자료실습실": (-12.9354133606,25.7812213898,0.993836150877,-0.110858942855),
            "인터넷 데이터베이스 실습실": (7.34447479248,28.6684932709,0.996912834196,-0.0785162468207),
            "서쌍희": (31.4291191101,10.8785123825,0.743004555214,0.669286359439),
            "김진호": (30.8621482849,16.0014648438,0.743991645201,0.668188919297),
            "정민수": (30.8621482849,16.0014648438,0.743991645201,0.668188919297),
            "임현일": (30.0773963928,24.5959434509,-0.681707664048,0.731624672068),
            "석승준": (30.0773963928,24.5959434509,-0.681707664048,0.731624672068),
            "공실": (28.2532978058,1.49982857704,0.0201580206609,0.999796806458),
            "황두영": (13.9487304688,29.2480068207,0.996792497087,-0.080029480516),
            "김영준": (3.73685979843,28.411441803,0.996393873801,-0.0848483839085),
            "시스템분석 실습실": (-2.63971590996,27.574262619,0.994234875398,-0.107224122953),
            "최형우": (-6.49700927734,26.900976181,0.9975272295,-0.0702810529626),
            "이현동": (-6.07907867432,25.9202823639,0.0748686013507,0.997193407786),
            "이기성": (-8.97193241119,25.7932567596,0.0773337202327,0.997005263635),
            "임지언": (-16.7935085297,25.2723865509,0.9954242278,-0.0955542082203),
            "전하영": (-19.5648956299,24.276309967,0.108025895974,0.994148080418),
            "이학준": (-19.5648956299,24.276309967,0.108025895974,0.994148080418),
            "박미영": (31.6432685852,6.5971326828,0.733228079123,0.679982782124),
            "컴퓨터 네트워크 실습실": (8.33035945892,27.9321670532,0.0803707754657,0.996765036732),
            "컴퓨터공학부 사무실": (-16.4710083008,24.6061325073,0.0891534420677,0.996017903337)
            }
# messages = []
# messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})

def move(member):
    for i in location.keys():
        if i in member:
            print("move x: ", location.get(i)[0], "move y: ", location.get(i)[1])
            return "~~FMG~~navi_{}_{}_{}_{}".format(location.get(i)[0], location.get(i)[1],location.get(i)[2],location.get(i)[3])
    return "~~FMG~~None"
def move_pepper(data):
    if "왼쪽" in data: 
        return "~~FMG~~left_move"
    if "오른쪽" in data: 
        return "~~FMG~~right_move"
    if "앞쪽" in data: 
        return "~~FMG~~front_move"
    if "뒤쪽" in data: 
        return "~~FMG~~back_move"
    if "랜덤" in data: 
        return "~~FMG~~random_move"
    

def dance():
    print("dance!!!!!!")
    return "~~FMG~~dance"

def clap():
    print("clap!!!!!!")
    return "~~FMG~~clap"


def rock_paper_scissors():
    print("rock_paper_scissors")
    return "~~FMG~~rock_paper_scissors"


def stop_behavior():
    print("stopstop!!")
    return "~~FMG~~stop_behavior"


def happy():
    return "~~FMG~~happy"


def sad():
    return "~~FMG~~sad"


def angry():
    return "~~FMG~~angry"

def zombi():
    return "~~FMG~~zombi"

def guitar():
    return "~~FMG~~guitar"

def faceage():
    return "~~FMG~~faceage"


def nothing():
    return "~~FMG~~nothing"

def stop_navigation():
    return "~~FMG~~stop_navigation"


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
    try:
        assistant_message = chat_response.choices[0].message
    except:
        assistant_message = "에러발생"
    print("assistant_message:" , assistant_message.content)
    send_message += "~~BMG~~" + str(assistant_message.content)

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
            messages.append({"role": "system", "content": "위치를 말해주고 직접 안내가 필요하냐고 물어보기. 만약 안내해달라고 하면, 사족 덧붙이지 말고 \"안내해드릴게요\" 라고 말하기."})
            member = tool_calls[0].function.arguments
            chat_use = True
        elif tool_function_name == "pepper_navigation":
            if "직접 안내 필요" in tool_calls[0].function.arguments:
                print(tool_calls[0].function.arguments)
                send_message += str(move(member))
                chat_use = True
        elif tool_function_name == "pepper_behavior":
            if "춤 추기" in tool_calls[0].function.arguments:
                messages.append({"role": "system", "content": "\"춤을 한번 춰볼게요!\"라고 말한다."})
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

        elif tool_function_name == "pepper_action":
            if "기타치기" in tool_calls[0].function.arguments:
                send_message += guitar()
            elif "좀비흉내내기" in tool_calls[0].function.arguments:
                send_message += zombi()     

        elif tool_function_name == "faceage":
                send_message += faceage()
        
        elif tool_function_name == "stop_navigation":
            if "안내 멈추기" in tool_calls[0].function.arguments:
                messages.append({"role": "system", "content": "안내를 멈춘다고 말한다."})
                send_message += stop_navigation()
                chat_use = True
        elif tool_function_name == "move":
            if "움직이기" in tool_calls[0].function.arguments:
                if "왼쪽" in tool_calls[0].function.arguments:
                    send_message += move_pepper("왼쪽")
                elif "오른쪽" in tool_calls[0].function.arguments:
                    send_message += move_pepper("오른쪽")   
                elif "앞쪽" in tool_calls[0].function.arguments:
                    send_message += move_pepper("앞쪽")
                elif "뒤쪽" in tool_calls[0].function.arguments:
                    send_message += move_pepper("뒤쪽")
                elif "랜덤" in tool_calls[0].function.arguments:
                    send_message += move_pepper("랜덤")
                messages.append({"role": "system", "content": "이동한다고 말한다."})
                chat_use = True


        if chat_use == True:
            try:                                
                chat_response = chat_completion_request(
                    messages=messages, tools=None, tool_choice=None
                )
                assistant_message = chat_response.choices[0].message
                print("assistant_message:" , assistant_message.content)
                send_message += "~~TMG~~" + str(assistant_message.content)
                chat_use = False
            except:
                pass
        chat_use = False
    print(send_message)
    socket.sendall(send_message.encode(encoding='utf-8'))

    if msg == '/end':
        break
    count += 1 