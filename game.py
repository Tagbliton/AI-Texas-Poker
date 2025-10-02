import os
import json
from volcenginesdkarkruntime import Ark
from pydantic import BaseModel  # 用于定义响应解析模型




def getfile(file):
    with open(file, 'r', encoding='utf-8') as f:
        results = f.read()
    return results


#Doubao

# 定义分步解析模型（对应业务场景的结构化响应）
class ID(BaseModel):
    name: str  # 玩家名称
    message: str       # 玩家私有信息


class MathResponse(BaseModel):
    id1: list[ID]       # 玩家信息列表
    id2: list[ID]
    id3: list[ID]
    public_messages: str   # 公共信息
    next_player_id: str   # 当前玩家名称
    remark_and_available_operations: str   #可用操作



client = Ark(
    # 从环境变量中读取您的方舟API Key
    api_key=os.environ.get("DOUBAO_API_KEY"),
    # 深度思考模型耗费时间会较长，请您设置较大的超时时间，避免超时，推荐30分钟以上
    timeout=1800,
    )
completion = client.beta.chat.completions.parse(
    # 替换 <Model> 为您的Model ID
    model="doubao-seed-1.6-250615",
    messages=[
        {"role": "system", "content": "你是一名德州扑克游戏的裁判，你需要分析附件的游戏日志，将日志提取为公开信息和每名玩家隐藏信息，公开信息为目前所有玩家已知信息，玩家隐藏信息为玩家手牌及剩余筹码，并将当前玩家及可选操作列出，输出为json"},
        {"role": "user", "content": getfile('poker_log.txt')}
    ],
    response_format=MathResponse,  # 指定响应解析模型
    extra_body={
        "thinking": {
            "type": "disabled"  # 不使用深度思考能力
            # "type": "enabled" # 使用深度思考能力
        }
    }
)
resp = completion.choices[0].message.parsed

print(resp.model_dump_json(indent=2))

with open('log.json', 'w', encoding='utf-8') as f:
    f.write(resp.model_dump_json(indent=2))
    print('信息整理完成，交由下一位选手操作')




import os
import json
from openai import OpenAI
from volcenginesdkarkruntime import Ark


#load rule
with open('rule/player_system.json', 'r', encoding='utf-8') as f:
    rule = f.read()
rule = json.loads(rule)
player1_rule = rule["player1"]
example = rule["example"]

#load messages
with open('log.json', 'r', encoding='utf-8') as f:
    messages = f.read()
messages = json.loads(messages)

#玩家信息
player1_message = messages["id1"][0]
player2_message = messages["id2"][0]
player3_message = messages["id3"][0]
#公共信息
public_messages = messages["public_messages"]
#本轮玩家
next_player_id = messages["next_player_id"]
#可用操作
remark_and_available_operations = messages["remark_and_available_operations"]

if next_player_id == "1":

    #Deepseek

    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": player1_rule + example},
            {"role": "user", "content": f"你的信息：{player1_message},当前场面信息{public_messages},当前可用操作：{remark_and_available_operations}"},
        ],
        stream=False
    )

    print(response.choices[0].message.content)

elif next_player_id == "2":

    #Qwen3

    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": player1_rule + example},
            {"role": "user", "content": f"你的信息：{player2_message},当前场面信息{public_messages},当前可用操作：{remark_and_available_operations}"},
        ],
        stream=True
    )
    for chunk in completion:
        print(chunk.choices[0].delta.content, end="", flush=True)


else:
    #Doubao

    client = Ark(
        # 从环境变量中读取您的方舟API Key
        api_key=os.environ.get("DOUBAO_API_KEY"),
        # 深度思考模型耗费时间会较长，请您设置较大的超时时间，避免超时，推荐30分钟以上
        timeout=1800,
        )
    response = client.chat.completions.create(
        # 替换 <Model> 为您的Model ID
        model="doubao-seed-1.6-250615",
        messages=[
            {"role": "system", "content": player1_rule + example},
            {"role": "user", "content": f"你的信息：{player3_message},当前场面信息{public_messages},当前可用操作：{remark_and_available_operations}"},
        ],
         thinking={
             "type": "disabled" # 不使用深度思考能力,
             # "type": "enabled" # 使用深度思考能力
             # "type": "auto" # 模型自行判断是否使用深度思考能力
         },
    )

    print(response.choices[0].message.content)
