import json
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored  

    #받은 메시지 GPT한테 전달
    content = msg
    messages.append({"role":"user", "content":content})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
        # model="gpt-4o", messages=messages
    )
    chat_response = completion.choices[0].message
    print('GPT msg: {chat_response}')
    msg2 = chat_response 
    print(msg2["content"])
    socket.sendall(msg2["content"].encode(encoding='utf-8'))